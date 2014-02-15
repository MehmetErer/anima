
import os
import pymel.core as pm


def create_shot_playblasts():
    """creates the selected shot playblasts
    """
    shots = pm.ls(sl=1, type=pm.nt.Shot)
    active_panel = pm.playblast(activeEditor=1)

    path_template = os.path.join(
        pm.workspace.name,
        'Outputs/Playblast/AllShots/'
    ).replace('\\', '/')

    filename_template = '%(scene)s_%(shot)s.mov'

    # template vars
    scene_name = os.path.basename(pm.env.sceneName()).split('.')[0]

    for shot in shots:
        shot_name = shot.name()
        start_frame = shot.startFrame.get()
        end_frame = shot.endFrame.get()
        width = shot.wResolution.get()
        height = shot.hResolution.get()

        rendered_path = path_template % {}
        rendered_filename = filename_template % {
            'shot': shot_name,
            'scene': scene_name
        }

        movie_full_path = os.path.join(
            rendered_path,
            rendered_filename
        ).replace('\\', '/')

        pm.playblast(
            fmt="qt",
            startTime=start_frame,
            endTime=end_frame,
            sequenceTime=1,
            forceOverwrite=1,
            filename=movie_full_path,
            clearCache=True,
            showOrnaments=False,
            percent=100,
            wh=[width, height],
            offScreen=True,
            viewer=0,
            useTraxSounds=True,
            compression="PNG",
            quality=70
        )
