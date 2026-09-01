select
    r.value:product_id::string as product_id,
    ai.index::number as ingredient_index,
    ai.value:name::string as ingredient_name,
    ai.value:strength::string as strength,
    src.source_file

from {{ source('pharma_raw', 'NDC_RAW') }} as src,
lateral flatten(input => src.raw_data:results) as r,
lateral flatten(input => r.value:active_ingredients) as ai