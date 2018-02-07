'''
To Run : 
"S:\BBF_PIPELINE\BBF\Common\Tools\Python\Python26_64\python.exe" c:\git_bbf\BBF_PIPELINE_dev\BBF\Common\Tools\Gateway\Src\BBF_Gateway_V2.py -nogui -app MAYA2016BATCH -project Vampirina2  -script "C:\git_bbf\BBF_PIPELINE_dev\BBF\Common\Tools\repath_tool\runner.mel"
'''

import shutil
import os
import time
import logging
from logging.config import fileConfig
import tempfile
import BBF
import BBF_environ
from bbfAssetRepo import bbfAssetRepo

import bbfCelery.svn as svn
from Utilities.bbfBatchProcess.PathRemap import PathRemap
from ShotgunInterface import ShotgunInterface
from . import processing_list


temp_folder = tempfile.mkdtemp(prefix="RepathTool_")
logger = logging.getLogger("RepathTool")
fhandler = logging.FileHandler("{0}/{1}.log".format(temp_folder, time.time()))
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.DEBUG)

exclude_path = ['J:/Productions/Vampirina2/AssetsRepo/Props\BagGarbage\Rig\VAM_P_Baggarbage_RG.ma',
                'J:/Productions/Vampirina2/AssetsRepo/Sets/MuseumInt/Model/VAM_S_MuseumInt_MDL_withCharacters.ma']
dummy_list  = ['BackstageSchool', "BackstageTransylvania", "BackyardsNight"]

def get_current_season_assets(project_name):
    shotgun = ShotgunInterface('BrownBagFilms-Eventless')
    shotgun.connect(project_name)

    assets={}
    for asset in shotgun.getEntityObjectList('Asset',['code','sg_season_','sg_link_to_previous_seasons_asset']):
        if asset.sg_season_=='Current':
            if asset.sg_link_to_previous_seasons_asset==None:
                assets[asset.code]=asset
            else:
                assets[asset.sg_link_to_previous_seasons_asset.name]=asset
    return assets

def run():
    processed_file_count = 0
    project_name='Vampirina2'
    src_folder='J:/Productions/Vampirina2/AssetsRepo'
    
    env = BBF_environ.loadEnv(project_name)
    BBF_environ.setEnv(env)
    repoClient = bbfAssetRepo()
    current_season_assets = get_current_season_assets(project_name)

    # startfile = None
    # if os.path.exists('current_scene.txt'):
    #     with open('current_scene.txt','r') as f:
    #         startfile =f.read()
    # start = not startfile 

    # Change below path accordingly!!
    for root, dirs, files in os.walk(src_folder + '/Sets'):
        for file_ in files:
            file_path = os.path.join(root, file_)
            extension = os.path.splitext(file_path.lower())[-1]
            relative_path = file_path[len(src_folder)+1:]
            relative_folders = relative_path.replace("\\", "/").split('/')

            # if startfile == os.path.basename(file_path):
            #     logger.info("Starting batch job with %s" % file_path)
            #     start = True
            #     with open('crashed_files.txt','a') as f:
            #         f.write(file_path)
            #     continue

            # if not start:
            #     continue
            if relative_folders[1].startswith('A') or relative_folders[1].startswith('B'):
                continue

            
            ts = svn.tasks.get_timestamp(file_path)
            try:

                log = repoClient.getLog(file_path)
                author = log[-1].author if log else ''
            except:
                print "Repath Tool: skiping {0}, failed to get log".format(file_path)
                continue

            if ts.split()[0] in ['2018-01-25', "2018-01-26", "2018-01-27", "2018-01-28", "2018-01-29", "2018-01-30", "2018-01-31"]:
                if author == 'liju.kunnummal':
                    print "Repath Tool : Skipping {0} - {1} and Done by Liju".format(file_path, ts)
                    continue

            if extension not in ['.ma','.mb']:
                continue
            
            if relative_folders[1] not in processing_list.process_list:
                continue

            if len(relative_folders)>=2 and (relative_folders[0] in ['Chars','Props','Sets'] and relative_folders[1] in current_season_assets):
                continue

            if relative_folders[1] in dummy_list:
                continue

            
            # with open('current_scene.txt','w') as f:
            #     f.write(os.path.basename(file_path))

            if file_path.replace("\\", "/") in  exclude_path:
                continue

            logger.info("Processing - {0} - {1}".format(file_path, ts))
            temp_location = "{0}/{1}".format(temp_folder, file_)
            shutil.copy(file_path,temp_location)
            # Repath
            PathRemap(scene=temp_location)
            # Check in file.
            repo_folder = root[len(src_folder)+1:]
            svn.checkin_file(project_name, repo_folder, temp_location, check_studio=False, comment='repath to Vampirina2 folder.')
            try:
                os.unlink(temp_location)
            except:
                pass
            logger.info("Processing Finished Successfully!")
            logger.info("========================================================")
            processed_file_count += 1

    logger.info("Number of processed files - {0}".format(processed_file_count))


run()