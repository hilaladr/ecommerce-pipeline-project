with orders as (
    select * from {{ ref('stg_orders')}}
),
    items as (
        select * from {{ ref('stg_items')}}
)

select 
   date(o.ORDER_PURCHASE_TIMESTAMP) as order_day,
   count(distinct o.ORDER_ID) as num_of_orders,
   sum(i.PRICE) as total_price
   from orders o, items i
   where o.order_id = i.order_id and o.order_status = 'delivered'
   group by order_day
