
site_count = FOREACH row GENERATE site, COUNT(trend) AS count;
STORE site_count INTO 'site_count.gz' USING JsonStorage();
