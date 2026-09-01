with products as (

    select *
    from {{ ref('stg_ndc_products') }}

),

packages as (

    select *
    from {{ ref('stg_ndc_packaging') }}

),

final as (

    select
        p.product_id,
        p.product_ndc,
        pk.package_ndc,

        case
            when regexp_like(pk.package_ndc, '^[0-9]{4}-[0-9]{4}-[0-9]{2}$')
                then
                    '0'
                    || split_part(pk.package_ndc, '-', 1)
                    || split_part(pk.package_ndc, '-', 2)
                    || split_part(pk.package_ndc, '-', 3)

            when regexp_like(pk.package_ndc, '^[0-9]{5}-[0-9]{3}-[0-9]{2}$')
                then
                    split_part(pk.package_ndc, '-', 1)
                    || '0'
                    || split_part(pk.package_ndc, '-', 2)
                    || split_part(pk.package_ndc, '-', 3)

            when regexp_like(pk.package_ndc, '^[0-9]{5}-[0-9]{4}-[0-9]{1}$')
                then
                    split_part(pk.package_ndc, '-', 1)
                    || split_part(pk.package_ndc, '-', 2)
                    || '0'
                    || split_part(pk.package_ndc, '-', 3)

            when regexp_like(pk.package_ndc, '^[0-9]{11}$')
                then pk.package_ndc

            else null
        end as ndc_canonical,

        p.brand_name,
        p.generic_name,
        p.labeler_name,
        p.dosage_form,
        p.product_type,
        p.marketing_category,

        pk.description as package_description,
        pk.is_sample,
        pk.marketing_start_date as package_marketing_start_date,
        pk.marketing_end_date as package_marketing_end_date

    from products p
    inner join packages pk
        on p.product_id = pk.product_id

)

select *
from final