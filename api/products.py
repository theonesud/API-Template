from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from config import app_logger
from core.slack import send_error_to_slack
from model.db import Product, get_session
from model.ql import EditProductRequest, ProductRequest

from .auth import get_user_from_token

router = APIRouter(prefix="/products")


@router.post("/")
async def create_product(product: ProductRequest, user=Depends(get_user_from_token)):
    try:
        product_id = str(uuid4())
        now = datetime.utcnow()
        new_product = Product(
            id=product_id,
            **product.dict(),
            created_at=now,
            updated_at=now,
        )

        async with get_session() as session:
            session.add(new_product)

        app_logger.info(f"Product created successfully: {product_id}")
        return {
            "message": "Product created successfully",
            "data": {"product_id": product_id},
        }
    except Exception as e:
        app_logger.exception(f"Error creating product: {e}")
        await send_error_to_slack(f"Error creating product: {e}")
        return HTTPException(status_code=500, detail="Error creating product")


@router.get("/")
async def get_products(user=Depends(get_user_from_token)):
    try:
        stmt = select(Product).filter(Product.deleted == False)
        async with get_session() as session:
            result = await session.execute(stmt)
            products = result.scalars().all()

        products_list = []
        for product in products:
            products_list.append(
                {
                    **product.__dict__,
                }
            )
        app_logger.info("Products retrieved successfully")
        return {
            "message": "Products retrieved successfully",
            "data": products_list,
        }
    except Exception as e:
        app_logger.exception(f"Error fetching products: {e}")
        await send_error_to_slack(f"Error fetching products: {e}")
        return HTTPException(status_code=500, detail="Error fetching products")


@router.get("/{id}")
async def get_product(id: str, user=Depends(get_user_from_token)):
    try:
        stmt = select(Product).filter(Product.id == id, Product.deleted == False)
        async with get_session() as session:
            result = await session.execute(stmt)
            product = result.scalar_one_or_none()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        product_dict = {
            **product.__dict__,
        }
        app_logger.info(f"Product {id} retrieved successfully")
        return {
            "message": "Product retrieved successfully",
            "data": product_dict,
        }
    except Exception as e:
        app_logger.exception(f"Error fetching product {id}: {e}")
        await send_error_to_slack(f"Error fetching product {id}: {e}")
        return HTTPException(status_code=500, detail=f"Error fetching product {id}")


@router.put("/{id}")
async def update_product(
    id: str, product: EditProductRequest, user=Depends(get_user_from_token)
):
    try:
        now = datetime.utcnow()
        product_data = product.dict(exclude_unset=True)

        async with get_session() as session:
            db_product = await session.get(Product, id)
            if not db_product:
                raise HTTPException(status_code=404, detail="Product not found")
            for key, value in product_data.items():
                setattr(db_product, key, value)
            db_product.updated_at = now

        app_logger.info(f"Product {id} updated successfully")
        return {"message": "Product updated successfully", "data": {"product_id": id}}
    except Exception as e:
        app_logger.exception(f"Error updating product {id}: {e}")
        await send_error_to_slack(f"Error updating product {id}: {e}")
        return HTTPException(status_code=500, detail="Error updating product")


@router.delete("/{id}")
async def delete_product(id: str, user=Depends(get_user_from_token)):
    try:
        now = datetime.utcnow()
        async with get_session() as session:
            db_product = await session.get(Product, id)
            if not db_product:
                raise HTTPException(status_code=404, detail="Product not found")
            db_product.deleted = True
            db_product.updated_at = now

        app_logger.info(f"Product {id} deleted successfully")
        return {"message": "Product deleted successfully", "data": {"product_id": id}}
    except Exception as e:
        app_logger.exception(f"Error deleting product {id}: {e}")
        await send_error_to_slack(f"Error deleting product {id}: {e}")
        return HTTPException(status_code=500, detail="Error deleting product")
