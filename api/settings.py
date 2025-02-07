from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from config import app_logger
from core.slack import send_error_to_slack
from model.db import Company, get_session
from model.ql import EditCompanyRequest

from .auth import get_user_from_token

router = APIRouter(prefix="/company")


@router.get("/{company_id}")
async def get_company(company_id: int, user=Depends(get_user_from_token)):
    try:
        async with get_session() as session:
            stmt = select(Company).filter(Company.id == company_id)
            result = await session.execute(stmt)
            company = result.scalar_one_or_none()
            company_dict = company.__dict__
            company_dict.pop("_sa_instance_state", None)
            app_logger.info(f"Company {company_id} retrieved successfully")
            return {"message": "Company retrieved successfully", "data": company_dict}
    except Exception as e:
        app_logger.error(f"Error fetching company {company_id}: {e}")
        await send_error_to_slack(f"Error fetching company {company_id}: {e}")
        return HTTPException(
            status_code=500, detail=f"Error fetching company {company_id}"
        )


@router.put("/{company_id}")
async def update_company(
    company_id: int, company: EditCompanyRequest, user=Depends(get_user_from_token)
):
    try:
        update_data = company.dict(exclude_unset=True)
        now = datetime.utcnow()
        update_data["updated_at"] = now

        async with get_session() as session:
            stmt = select(Company).where(Company.id == company_id)
            result = await session.execute(stmt)
            db_company = result.scalar_one_or_none()
            for key, value in update_data.items():
                setattr(db_company, key, value)
        app_logger.info(f"Company {company_id} updated successfully")
        return {
            "message": "Company updated successfully",
            "data": {"company_id": company_id},
        }

    except Exception as e:
        app_logger.error(f"Error updating company {company_id}: {e}")
        await send_error_to_slack(f"Error updating company {company_id}: {e}")
        return HTTPException(
            status_code=500, detail=f"Error updating company {company_id}"
        )
