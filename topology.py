def path_bfs(event,dst_mac):
  """
  Get list of ports to get a path to a mac from a packet in
  Uses Breadth First Search
  """
  # Get the location of the dst_mac
  dst_entry = get_mac_entry(dst_mac)
  dst_links = get_links_by_dpid(dst_entry.dpid)
  # BFS
  queue = [ ]
  print "==="
  print dst_links.a_dpid
  queue.append(dst_links)
  
  return 
  while queue:
    # Does dpid of queue 
    path = queue.pop(0)
    # get last node
    node = path[-1]
    # if node is src - path found
    if (node.a_dpid == event.dpid) or (node.z_dpid == event.dpid): 
       return path
    # enumerate all nodes at level
    links = get_links_by_dpid(node.a_dpid)
    for next_entries in links:
       new_path = list(path)
       new_path.append(next_entries)
       queue.append(new_path)