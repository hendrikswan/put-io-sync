def print_items(items):
  for it in items:
    print it.id, it.name
    reflect_item(it)
      
def reflect_item(item):
  for property, value in vars(item).iteritems():
    print "\t", property, ':', value 