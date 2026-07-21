use  hr_data_analysis;
select*from general_data;
select*from employee_survey;
select*from manager_survey;

alter table general_data
drop column employeecount;

alter table general_data
drop column over18;

alter table general_data
drop column education;

WITH RankedData AS (
    SELECT 
        NumCompaniesWorked,
        ROW_NUMBER() OVER (ORDER BY NumCompaniesWorked) as row_num,
        COUNT(*) OVER () as total_rows
    FROM general_data
    WHERE NumCompaniesWorked IS NOT NULL
)
SELECT AVG(NumCompaniesWorked) AS median_value
FROM RankedData
WHERE row_num IN (FLOOR((total_rows + 1) / 2), CEIL((total_rows + 1) / 2));

UPDATE  general_data
SET NumCompaniesWorked = CAST(2 AS UNSIGNED)
WHERE NumCompaniesWorked =0 ;

SET SQL_SAFE_UPDATES=0;

SELECT COUNT(NumCompaniesWorked)
FROM general_data
where NumCompaniesWorked=0;

select *from general_data
where
TotalWorkingYears >= 20
AND NumCompaniesWorked = 0;

select *from general_data
where
YearsAtCompany > TotalWorkingYears;
-- 1
SELECT COUNT(*)
FROM general_data
WHERE YearsAtCompany > TotalWorkingYears;

-- 2
SELECT COUNT(*)
FROM general_data
WHERE Age < TotalWorkingYears;

-- 3
SELECT COUNT(*)
FROM general_data
WHERE MonthlyIncome <= 0;

-- 4
SELECT COUNT(*)
FROM general_data
WHERE TotalWorkingYears < 0;	

-- 5
SELECT COUNT(*)
FROM general_data
WHERE NumCompaniesWorked < 0;

SELECT COUNT(*) AS total_duplicate_ids
FROM (
    SELECT EmployeeID
    FROM general_data
    GROUP BY EmployeeID
    HAVING COUNT(EmployeeID) > 1
) AS duplicate_counts;
------------------------------------
select*from general_data 
where monthlyincome<0;

select*from general_data
where age<18;

select attrition,count(attrition) from
general_data
group by attrition;

select gender,count(gender)
from general_data
group by gender;
------------------------------------
select count(employeeid) as totalemployee
from general_data;

select department
 from 
general_data 
group by department;

select distinct jobrole from
general_data;

select avg(age) as avg_age
from general_data;

select 
max(monthlyincome) as maximum,
min(monthlyincome) as minimum
from general_data;

select gender,count(gender)
from general_data
group by gender;

select 
department,
count(employeeid) as total_employees
from general_data
group by department
order by total_employees desc ;

select 
educationfield , 
count(employeeid) as total_employees
from general_data
group by educationfield
order by total_employees desc;

select 
businesstravel ,
count(employeeid) as total_employees
from general_data
group by businesstravel
order by total_employees desc;

select
attrition , 
count(employeeid) as total_employees
from general_data
group by attrition 
order by total_employees desc;

select *
from general_data
where age>30;

update  general_data
set department = 'HR'
where department ='Human Resources';

update general_data
set department ='R&D'
where department ='Research & Development';

select *
from general_data
where department='HR';

alter table general_data
rename column Monthlyincome to salary;

select*
from general_data
where salary > 5000;

select *
from general_data
where maritalstatus = 'Married';

select*
from general_data
where gender= 'male' and department='sales';

select*
from general_data
where TotalWorkingYears > 10;

select*
from general_data
where age between 25 and 35;

select employeeid, salary
from 
(select *,
dense_rank() over(order by salary asc) as denrnk from general_data)t
where denrnk<10
limit 10;

select employeeid,salary
from general_data
order by salary desc
limit 10;


select *
from general_data
where jobrole='manager';

select*
from
(select *,dense_rank() over(partition by department order by salary desc ) as densrnk
from general_data)t
where densrnk<=3
order by department ,salary desc;

SELECT  Age,
       Attrition,
       BusinessTravel,
       Department,
       DistanceFromHome,
       EducationField,
       Gender,
       JobLevel,
       JobRole,
       MaritalStatus,
       Salary,
       NumCompaniesWorked,
       PercentSalaryHike,
       StockOptionLevel,
       TotalWorkingYears,
       TrainingTimesLastYear,
       YearsAtCompany,
       YearsSinceLastPromotion,
       YearsWithCurrManager,
       COUNT(*) AS total
FROM general_data
GROUP BY
       Age,
       Attrition,
       BusinessTravel,
       Department,
       DistanceFromHome,
       EducationField,
       Gender,
       JobLevel,
       JobRole,
       MaritalStatus,
       Salary,
       NumCompaniesWorked,
       PercentSalaryHike,
       StockOptionLevel,
       TotalWorkingYears,
       TrainingTimesLastYear,
       YearsAtCompany,
       YearsSinceLastPromotion,
       YearsWithCurrManager
       HAVING COUNT(*) > 1;
       
SELECT COUNT(*)
FROM general_data
GROUP BY EmployeeID
HAVING COUNT(*) > 1;
SELECT COUNT(*) AS total_duplicate_groups
FROM (
    SELECT
        Age,
        Attrition,
        BusinessTravel,
        Department,
        DistanceFromHome,
        EducationField,
        Gender,
        JobLevel,
        JobRole,
        MaritalStatus,
        Salary,
        NumCompaniesWorked,
        PercentSalaryHike,
        StockOptionLevel,
        TotalWorkingYears,
        TrainingTimesLastYear,
        YearsAtCompany,
        YearsSinceLastPromotion,
        YearsWithCurrManager
    FROM general_data
    GROUP BY
        Age,
        Attrition,
        BusinessTravel,
        Department,
        DistanceFromHome,
        EducationField,
        Gender,
        JobLevel,
        JobRole,
        MaritalStatus,
        Salary,
        NumCompaniesWorked,
        PercentSalaryHike,
        StockOptionLevel,
        TotalWorkingYears,
        TrainingTimesLastYear,
        YearsAtCompany,
        YearsSinceLastPromotion,
        YearsWithCurrManager
    HAVING COUNT(*) > 1
) t;
-----------------------------------------
select
 department
 ,round(avg(salary),2) as avgsalary
 from general_data
 group by department
 order by avgsalary desc;
 
 select
 department,
 max(salary) as maximum_salary 
 from general_data
 group by department
 order by maximum_salary desc;
 
  select
 department,
 MIN(salary) as minimum_salary 
 from general_data
 group by department
 order by minimum_salary desc;
 
 select
 department,
 count(attrition) as total_attrition
 from general_data
 group by department
 order by total_attrition desc;

SELECT 
department,
COUNT(CASE WHEN attrition = 'Yes' THEN 1 END) AS attrition_count,
COUNT(employeeid) AS total_employees,
ROUND((COUNT(CASE WHEN attrition = 'Yes' THEN 1 END) / COUNT(*)) * 100, 2) AS attrition_rate_percent
FROM general_data
GROUP BY department
ORDER BY attrition_rate_percent DESC;

select 
jobrole,
round(Avg(salary),2) as avg_salary
from general_data
group by jobrole
order by avg_salary desc;

select 
jobrole,
round(Avg(salary),2) as avg_salary
from general_data
group by jobrole
order by avg_salary desc
limit 5;

select 
department,
round(avg(age)) as avg_age
from general_data
group by department
order by avg_age desc;

select
department,
avg(TotalWorkingYears) as avg_work
from general_data
group by department
order by avg_work desc;

select
MaritalStatus,
round(avg(salary),2) as avg_salary
from general_data
group by maritalstatus
order by avg_salary desc;

select 
department,
count(employeeid) as employeecount
from general_data
group by department
having  employeecount>1000;

select 
jobrole,
avg(salary) as total_avg
from general_data
group by jobrole
having total_avg>80000;

select 
EducationField,
avg(salary) as total_avg
from general_data
group by educationfield
having total_avg > 70000;

select 
department,
avg(TotalWorkingYears) as avg_exp
from general_data
group by department
having avg_exp > 10;

select 
BusinessTravel,
count(employeeid) as totalemp
from general_data
group by businesstravel
having totalemp > 500;

select*,
case
 when salary<30000 then 'low' 
 when salary>=30000 or salary<70000 then  'medium'
 else 'high'
 end as salary_level
 from general_data;
 

 select*,
 case 
 when age <30 then 'young'
 when age>=30 or age<45 then 'adult'
 else 'senior' 
 end 
 as avg_age
 from general_data;

select*,
case 
when TotalWorkingYears<=2 then 'fresher'
when TotalWorkingYears<3 or TotalWorkingYears>10 then 'mid level'
else 'experienced'
end
as experience_level
from general_data;

select department,employeeid,salary
from general_data g 
where salary >(select avg(salary) as department_avg from general_data 
                where department=g.department)
order by salary desc;

select *
from 
(select*, row_number() over(partition by department order by salary desc) as salary_order 
 from general_data)t
 where salary_order<=3
 order by department,salary desc;
 
 --------------
 select max(salary) 
 from general_data
 where salary<(select max(salary) from general_data);
 
 select *
from 
(select*, row_number() over(partition by department order by salary desc) as salary_order 
 from general_data)t
 where salary_order<=3
 order by department,salary desc;
-------------------------------------------------
 select g.employeeid,g.department,g.salary
 ,e.EnvironmentSatisfaction
 from general_data g
 left join employee_survey e
 on g.employeeid=e.employeeid
 order by g.employeeid;
 
 select g.employeeid,g.department,e.JobSatisfaction
 from general_data g 
 left join employee_survey e
 on g.employeeid=e.employeeid
 order by g.employeeid asc;
  
select g.employeeid,g.department,m.performancerating
from manager_survey m
right join general_data g
on m.employeeid=g.employeeid
order by g.employeeid asc;
 
 select g.department,avg(e.EnvironmentSatisfaction) as totalavg
 from employee_survey e
 right join general_data g
 on g.employeeid=e.employeeid
 group by g.department 
 order by totalavg desc;
 
 select g.department, avg(e.JobSatisfaction) as totalavg
 from employee_survey e
 right join general_data g
 on e.employeeid=g.employeeid
 group by g. department
 order by totalavg desc;
 
 select m.PerformanceRating,
 count(g.employeeid) as total_employee,
avg(g.salary) as avg_salary
from general_data g
left join manager_survey m
on g.employeeid=m.employeeid
group by m.PerformanceRating
order by avg_salary desc, total_employee desc;
 
 
 select*
 from
 (select row_number() over(order by salary desc) as salaryrnk,
 g.employeeid,g.department, g.jobrole,g.salary ,
 m.performancerating,e.EnvironmentSatisfaction,
 e.JobSatisfaction 
 from general_data g
 left join manager_survey m
 on g.employeeid=m.employeeid
 left join employee_survey e
 on m.employeeid=e.employeeid)t
 where salaryrnk <=10;
 
 
 
WITH CTE_DepartmentAverage AS (
SELECT g.employeeid, g.department, g.salary,
e.EnvironmentSatisfaction,
AVG(g.salary) OVER(PARTITION BY g.department) AS avg_dept_salary
FROM general_data g 
LEFT JOIN employee_survey e 
ON g.employeeid = e.employeeid
)
SELECT 
EnvironmentSatisfaction,department,
salary
FROM CTE_DepartmentAverage
WHERE EnvironmentSatisfaction < 3 
AND salary > avg_dept_salary;

