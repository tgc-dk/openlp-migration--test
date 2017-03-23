OpenLP 2.4.6
============

* Fixed a bug where the author type upgrade was being ignore because it was looking at the wrong table
* Fixed a bug where the songs_songbooks table was not being created because the if expression was the wrong way round
* Changed the songs_songbooks migration SQL slightly to take into account a bug that has (hopefully) been fixed
* Sometimes the timer goes off as OpenLP is shutting down, and the application has already been deleted (reported via support system)
* Fix opening the data folder (KDE thought the old way was an SMB share)
* Fix a problem with the new QMediaPlayer not controlling the playlist anymore
* Added importing of author types to the OpenLP 2 song importer
* Refactored the merge script and gave it some options
