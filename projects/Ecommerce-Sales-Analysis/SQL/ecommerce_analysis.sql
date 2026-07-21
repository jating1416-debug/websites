use datasets;
SELECT * FROM datasets.ecommerce_sales_data_2024_2025;
select*from ecommerce;

alter table ecommerce
rename column `sub-category` to sub_category;

alter table ecommerce
rename column `unit price` to unit_price;

alter table ecommerce
rename column `product name` to product_name;

alter table ecommerce
rename column `payment mode` to payment_mode;

alter table ecommerce
rename column `order date` to order_date;

alter table ecommerce
rename column `customer name` to customer_name;

alter table ecommerce
rename column `order id` to order_id;

select count(order_id)
from ecommerce;

select* from ecommerce
limit 10;

select distinct(category)from ecommerce;
select distinct(region) from ecommerce;
select max(profit) as maximum,
min(profit) as minimum
from ecommerce;

select category,round(sum(sales),2) as totalsales
from ecommerce 
group by category
order by totalsales desc
limit 10;

select count(distinct`product name`)from ecommerce;

select product_name,round(sum(sales),2) as totalsales
from ecommerce 
group by product_name
order by totalsales desc
limit 10;


select product_name, sum(profit) as totalprofit
from ecommerce 
group by product_name
order by totalprofit desc
limit 10;

select category, totalsales,totalprofit,
round((totalprofit/totalsales)*100) as profitmargin
from
(select category,
round(sum(sales))as totalsales ,
round(sum(profit)) as totalprofit
from ecommerce 
group by category )t
order by profitmargin desc ;

SELECT
    category,
    ROUND(SUM(sales),2) AS total_sales,
    ROUND(SUM(profit),2) AS total_profit,
    ROUND((SUM(profit)/SUM(sales))*100,2) AS profit_margin
FROM ecommerce
GROUP BY category
ORDER BY profit_margin DESC;


select region ,
round(sum(sales),2)as totalsales,
round(sum(profit),2) as totalprofit,
ROUND((SUM(profit)/SUM(sales))*100,2) AS profit_margin
from ecommerce 
group by region
order by profit_margin desc;

select 
city,
round(sum(sales),2)as city_totalsales
from ecommerce
group by city
order by city_totalsales desc
limit 10;

select 
city,
round(sum(profit),2)as city_totalprofit
from ecommerce
group by city
order by city_totalprofit desc
limit 10;

alter table ecommerce
rename column `payment mode` to payment_mode;

select
payment_mode,
count(payment_mode) as totalcount,
round(sum(sales),2) as sum_paymentmode
from ecommerce
group by payment_mode
order by totalcount desc,sum_paymentmode desc;


select
customer_name,
round(sum(sales),2) as totalsale
from ecommerce
group by customer_name
order by totalsale desc
limit 10;

select
customer_name,
round(sum(profit),2) as totalprofit
from ecommerce
group by customer_name
order by totalprofit desc
limit 10;

select 
category,
count(order_id) as totalcount
from ecommerce 
group by category
order by totalcount desc;

select 
round(sum(sales),2) as totalsales,
count(order_id) as totalorders,
round(round(sum(sales),2)/count(order_id),2) as averagesale
from ecommerce
order by averagesale desc;

select
round(sum(profit),2) as totalprofit,
count(order_id) as totalorder,
round(round(sum(profit),2)/count(order_id),2) as averageprofit
from ecommerce
order by averageprofit;

select
region,
count(order_id) as totalorder
from ecommerce
group by region 
order by totalorder desc;

select
category,
round(avg(discount),2) as avgdiscount
from ecommerce
group by category
order by avgdiscount desc;

select 
category,
round(sum(sales),2) as totalsales,
round(sum(profit),2) as totalprofit
from ecommerce
group by category
order by totalsales desc, totalprofit asc
limit 5;

select
city,
round(sum(sales),2) as totalsales,
round(sum(profit),2) as totalprofit
from ecommerce
group by city
order by totalsales desc, totalprofit desc
limit 5;



select
date_format(order_date,'%b')as month_wisesales,
round(sum(sales),2) as totalsales,
round(sum(profit),2) as totalprofit
from ecommerce
group by month_wisesales
order by totalsales;


select
category,product_name, sales ,rnk
from
(select 
category, product_name,sales,
row_number() over(partition by category order by sales desc) as rnk
from ecommerce)t
where rnk<=3
order by category
, sales desc;


select
category,product_name, profit,rnk
from
(select 
category, product_name,profit,
row_number() over(partition by category order by profit desc) as rnk
from ecommerce)t
where rnk<=3
order by category
, profit desc;
 


