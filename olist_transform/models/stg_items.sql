select
	ORDER_ID ,
	ORDER_ITEM_ID,
	PRODUCT_ID ,
	SELLER_ID ,
	try_to_timestamp(SHIPPING_LIMIT_DATE) as SHIPPING_LIMIT_DATE,
	PRICE ,
	FREIGHT_VALUE
from {{source('raw_source', 'ORDER_ITEMS')}}