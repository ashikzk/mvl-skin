import os
import time

try:
    #read screen_lock files content
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'screen_lock.dat')
    f = open(file_path, 'r')
    content = f.read()
    f.close()
    
    if len(content) == 0:    
        #if screen_lock doesn't have any content, that means we are good to go
        path = xbmc.getInfoLabel('Container.FolderPath')
        # print "PATH (OLD)  = " + path

        xbmc.executebuiltin( "Action(back)" )
        time.sleep(0.2)

        path_new = xbmc.getInfoLabel('Container.FolderPath')
        # print "PATH (NEW) = " + path_new

        #save new path and set it as current location path
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'screen_path.dat')
        f = open(file_path, 'w')
        f.write(path_new)
        f.close()


        if len(path.split('/')) >= 6 and path_new != path:
            #make sure path has changed cause in case of context menu, path doesn't change and view shouldn't change then
            selection = path.split('/')[3]
            selection_id = path.split('/')[4]
            page_num = path.split('/')[5]

            if selection == 'categories' and (selection_id == '1' or selection_id == '3'):
                #we are in screen 1, set view mode to 58
                xbmc.executebuiltin( "Container.SetViewmode(58)" )
                #clear current section name
                xbmc.executebuiltin('Skin.SetString(CurrentSection,)')
            elif (
                    selection == 'categories' and (selection_id == '23' or selection_id == '104916' or selection_id == '112504' or 
                    selection_id == '32' or selection_id == '104917' or selection_id == '366042' or selection_id == '372395' or selection_id == '372396') and
                    page_num == '0'
                 ) or selection == 'azlisting' or selection == 'search':
                #we are in screen 2, set view mode to 59
                xbmc.executebuiltin( "Container.SetViewmode(59)" )


except Exception, e:
    pass


