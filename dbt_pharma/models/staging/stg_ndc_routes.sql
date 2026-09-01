select
    r.value:product_id::string as product_id,
    rt.index::number as route_index,
    rt.value::string as route,
    src.source_file

from {{ source('pharma_raw', 'NDC_RAW') }} as src,
lateral flatten(input => src.raw_data:results) as r,
lateral flatten(input => r.value:route) as rt