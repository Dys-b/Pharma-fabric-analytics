select
    r.value:product_ndc::string        as product_ndc,
    r.value:product_id::string         as product_id,
    r.value:brand_name::string         as brand_name,
    r.value:brand_name_base::string    as brand_name_base,
    r.value:brand_name_suffix::string  as brand_name_suffix,
    r.value:generic_name::string       as generic_name,
    r.value:labeler_name::string       as labeler_name,
    r.value:dosage_form::string        as dosage_form,
    r.value:product_type::string       as product_type,
    r.value:marketing_category::string as marketing_category,
    r.value:application_number::string as application_number,
    r.value:dea_schedule::string       as dea_schedule,
    r.value:finished::boolean          as finished,

    try_to_date(
        r.value:marketing_start_date::string,
        'YYYYMMDD'
    ) as marketing_start_date,

    try_to_date(
        r.value:marketing_end_date::string,
        'YYYYMMDD'
    ) as marketing_end_date,

    try_to_date(
        r.value:listing_expiration_date::string,
        'YYYYMMDD'
    ) as listing_expiration_date,

    src.source_file

from {{ source('pharma_raw', 'NDC_RAW') }} as src,
lateral flatten(input => src.raw_data:results) as r