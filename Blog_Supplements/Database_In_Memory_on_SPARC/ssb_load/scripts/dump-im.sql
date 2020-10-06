select v.segment_name	name,
	v.populate_status	populate_status,
	v.bytes_not_populated	missing_bytes
from v$im_segments 	v
order by 1;
