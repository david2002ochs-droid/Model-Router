-- These are language-model image INPUT costs, not image-generation prices.
CREATE VIEW IF NOT EXISTS model_image_input_prices AS
SELECT source_url,page_sha256,retrieved_at_utc,model_id,model_slug,model_name,effort,
json_extract(model_json,'$.creator.name') AS model_creator_name,
json_extract(model_json,'$.priceDataSource.providerName') AS pricing_provider_name,
json_extract(model_json,'$.pricePer1k1mpImages') AS input_price_usd_per_1000_1mp_images,
json_extract(model_json,'$.pricePer1k1mpImages')/1000.0 AS input_price_usd_per_1mp_image_inferred
FROM embedded_latest_models WHERE json_type(model_json,'$.pricePer1k1mpImages') IN ('real','integer');
