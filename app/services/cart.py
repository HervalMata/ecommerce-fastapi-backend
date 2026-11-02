from decimal import Decimal

from sqlmodel import Session, select
from app.core.exceptions import ApiException
from app.models.cart import Cart, CartItem
from sqlalchemy.orm import selectinload
from fastapi import status
from app.models.product import Product

async def get_or_create_cart(db: Session, user_id: int) -> Cart:
    statement = (
        select(Cart).where(Cart.user_id == user_id).options(selectinload(Cart.items).selectinload(CartItem.product))
    )
    result = await db.exec(statement)
    cart = result.first()

    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)
        return await get_or_create_cart(db, user_id)

    if cart.items:
        cart.items.sort(key=lambda item: item.id)

    return cart

async def add_item_to_cart(db: Session, user_id: int, product_id: int, quantity: int):
    cart = await get_or_create_cart(db, user_id)            

    product = await db.get(Product, product_id)

    if not product:
        raise ApiException("Produto não encontrado", status.HTTP_404_NOT_FOUND)

    item_statement = select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
    item_result = await db.exec(item_statement)
    cart_item = item_result.first()    

    current_qty_in_cart = cart_item.quantity if cart_item else 0
    requested_total = current_qty_in_cart + quantity

    if product.stock_quantity < requested_total:
        raise ApiException(
            f"Não foi possivel adicionar {quantity}. Você já tem {current_qty_in_cart} no carrinho,"
            f"e somente {product.stock_quantity} no total estão no estoque.",
            status.HTTP_400_BAD_REQUEST
        )

    if cart_item:
        cart_item.quantity = requested_total
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)       
        db.add(cart_item) 

    await db.commit()
    return True

async def decrement_item_quantity(db: Session, user_id: int, product_id: int):   
    cart = await get_or_create_cart(db, user_id) 

    statement = select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == product_id)     
    result = await db.exec(item_statement)
    cart_item = item_result.first()  

    if not cart_item:
        raise ApiException("Item não encontrado no carrinho", status.HTTP_404_NOT_FOUND)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
    else:
        await db.delete(cart_item)
    await db.commit()
    return True    

async def remove_item_from_cart(db: Session, user_id: int, product_id: int):      
    cart = await get_or_create_cart(db, user_id) 

    statement = select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == product_id) 

    result = await db.exec(statement)
    item = result.first()

    if item:
        await db.delete(item)
        await db.commit()

    return True

async def clear_user_cart(db: Session, user_id: int):      
    cart = await get_or_create_cart(db, user_id)   

    for item in cart.items:
        await db.delete(item)
                
    await db.commit()
    return True

async def get_user_cart(db: Session, user_id: int):      
    cart = await get_or_create_cart(db, user_id)   

    items_data = []
    total_price = Decimal("0.0")
    total_qty = 0

    for item in cart.items:
        subtotal = item.product.price * item.quantity
        items_data.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": item.product.name,
            "product_price": item.product.price,
            "product_image": item.product.image_url,
            "quantity": item.quantity,
            "subtotal": subtotal,
        })
        total_price += subtotal
        total_qty += item.quantity

    return {
        "id": cart.id,
        "user_id": cart.user_id,
        "items": items_data,
        "total_quantity": total_qty,
        "total_price": total_price
    }    
