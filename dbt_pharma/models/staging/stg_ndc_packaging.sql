select
    r.value:product_id::string as product_id,
    p.index::number as package_index,
    p.value:package_ndc::string as package_ndc,
    p.value:description::string as description,

    try_to_date(
        p.value:marketing_start_date::string,
        'YYYYMMDD'
    ) as marketing_start_date,

    try_to_date(
        p.value:marketing_end_date::string,
        'YYYYMMDD'
    ) as marketing_end_date,

    p.value:sample::boolean as is_sample,
    src.source_file

from {{ source('pharma_raw', 'NDC_RAW') }} as src,
lateral flatten(input => src.raw_data:results) as r,
lateral flatten(input => r.value:packaging) as p