{% macro default__test_unique(model, column_name) %}

with validation_errors as (

    select {{ column_name }}
    from {{ model }}
    where {{ column_name }} is not null
    group by {{ column_name }}
    having count(*) > 1

)

select *
from validation_errors

{% endmacro %}
