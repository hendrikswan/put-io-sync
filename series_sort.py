#!/usr/bin/python
# Written by Deon Spengler

import os
import sys
import re
import shutil
from distutils import dir_util

class SortSeries():
    def __init__(self, basepath, newpath):
        self.basepath = basepath
        self.newpath = newpath
        self.seriesRegex = re.compile(r'(?P<series>[0-9a-zA-Z \._-]+)[ \._-](s|)(?P<season>\d{1,2})(e|x|)(?P<episode>\d{2})([\. -.+].+|)(?P<extension>\.avi$|\.mov$|\.mkv$|\.mp4$|\.ogm$)',  re.IGNORECASE)

    def sort(self):
        for (path, dirs, files) in os.walk(self.basepath):
            for file in files:
                videoFile = os.path.join(path,file)
                seriesMatch = self.seriesRegex.search(videoFile)

                if seriesMatch:
                    seriesName = seriesMatch.group('series').title().replace("-", " ").replace(".", " ")
                    seriesSeason = '%0*d' % (2, int(seriesMatch.group('season')))
                    seriesEpisode = seriesMatch.group('episode')
                    seriesExtension = seriesMatch.group('extension')

                    # Check if destination directory exists
                    desDir = os.path.join(self.newpath, seriesName, "Season-" + seriesSeason)
                    if os.path.exists(desDir) == False:
                        dir_util.mkpath(desDir)

                    newPath = os.path.join(desDir, '%s-S%sE%s%s' % (seriesName, seriesSeason, seriesEpisode, seriesExtension))

                    print 'Busy processing: %s-S%sE%s' % (seriesName, seriesSeason, seriesEpisode)
                    
                    # Copy and rename video file to new directory
                    shutil.copy(videoFile, newPath)
                    
                    os.remove(videoFile)
                    

if __name__=="__main__":
  if len(sys.argv) == 3:
      if os.path.isdir(sys.argv[1]) == False:
          print '\nSource directory "%s" does not exist\n' % sys.argv[1]
      elif os.path.isdir(sys.argv[2]) == False:
          print '\nDestination directory "%s" does not exist\n' % sys.argv[2]
      else:
          series = SortSeries(sys.argv[1], sys.argv[2])
          series.sort()
          print '\n    Finnished sorting your series.\n'
  else:
      print("\nUsage: sortseries source_directory destination_directory\n")
