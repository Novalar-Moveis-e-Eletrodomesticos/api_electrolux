SELECT
    client_id,
    client_secret,
    "name"
FROM public.users_api_electrolux
WHERE client_id = :idclient AND is_active IS TRUE;