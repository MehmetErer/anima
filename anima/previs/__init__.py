# -*- coding: utf-8 -*-
# Copyright (c) 2012-2014, Anima Istanbul
#
# This module is part of anima-tools and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause
from contextlib import contextmanager

import os
import subprocess
import tempfile
import pymel

import anima.extension.maya
from anima.extension import extends


class PrevisBase(object):
    """The base for other Previs classes
    """

    def from_xml(self, xml_node):
        """Fills attributes with the given XML node

        :param xml_node: an xml.etree.ElementTree.Element instance
        """
        raise NotImplementedError

    def to_xml(self, indentation=2, pre_indent=0):
        """returns an xml version of this PrevisBase object
        """
        raise NotImplementedError

    def from_edl(self, edl_list):
        """Fills attributes with the given edl.List instance

        :param edl_list: an edl.List instance
        """
        raise NotImplementedError

    def to_edl(self):
        """returns an EDL version of this PrevisBase object
        """
        raise NotImplementedError


class NameMixin(object):
    """A mixin for name attribute
    """

    def __init__(self, name=''):
        self._name = self._validate_name(name)

    @classmethod
    def _validate_name(cls, name):
        """validates the given name value
        """
        if not isinstance(name, str):
            raise TypeError(
                '%(class)s.name should be a string, not %(name_class)s' % {
                    'class': cls.__name__,
                    'name_class': name.__class__.__name__
                }
            )
        return name

    @property
    def name(self):
        """returns the _name attribute
        """
        return self._name

    @name.setter
    def name(self, name):
        """setter for the name property
        """
        self._name = self._validate_name(name)


class DurationMixin(object):
    """A mixin for duration attribute
    """

    def __init__(self, duration=0.0):
        self._duration = self._validate_duration(duration)

    @classmethod
    def _validate_duration(cls, duration):
        """validates the given duration value
        """
        if duration is None:
            duration = 0.0

        if not isinstance(duration, (int, float)):
            raise TypeError(
                '%(class)s.duration should be an non-negative float, not '
                '%(duration_class)s' % {
                    'class': cls.__name__,
                    'duration_class': duration.__class__.__name__
                }
            )

        duration = float(duration)

        if duration < 0:
            raise ValueError(
                '%(class)s.duration should be an non-negative float' % {
                    'class': cls.__name__
                }
            )

        return duration

    @property
    def duration(self):
        """returns the _duration attribute value
        """
        return self._duration

    @duration.setter
    def duration(self, duration):
        self._duration = self._validate_duration(duration)


class SequenceManagerExtension(object):
    """Extension to the pymel.core.nodetypes.SequenceManager class
    """

    @extends(pymel.core.nodetypes.SequenceManager)
    def get_shot_name_template(self):
        """returns teh shot_name_template_ attribute value, creates the
        attribute if missing
        """
        if not self.hasAttr('shot_name_template'):
            default_template = '<Sequence>_<Shot>_<Version>'
            self.set_shot_name_template(default_template)

        return self.shot_name_template.get()

    @extends(pymel.core.nodetypes.SequenceManager)
    def set_shot_name_template(self, template):
        """sets the shot_name_template attribute value
        """
        if not self.hasAttr('shot_name_template'):
            self.addAttr('shot_name_template', dt='string')

        self.shot_name_template.set(template)


    @extends(pymel.core.nodetypes.SequenceManager)
    def get_version(self):
        """returns the version attribute value, creates the attribute if
        missing
        """
        if not self.hasAttr('version'):
            self.set_version('')
        return self.version.get()

    @extends(pymel.core.nodetypes.SequenceManager)
    def set_version(self, template):
        """sets the version attribute value
        """
        if not self.hasAttr('version'):
            self.addAttr('version', dt='string')

        self.version.set(template)

    @extends(pymel.core.nodetypes.SequenceManager)
    def create_sequence(self, name=None):
        """Creates a new sequence

        :return: pymel.core.nodetypes.Sequence
        """
        sequencer = pymel.core.createNode('sequencer')
        if name:
            sequencer.set_sequence_name(name)

        sequencer.message >> self.sequences.next_available
        return sequencer

    @extends(pymel.core.nodetypes.SequenceManager)
    def from_xml(self, path):
        """Parses XML file and returns a Sequence instance which reflects the
        whole timeline hierarchy.

        :param path: The path of the XML file
        :return: :class:`.Sequence`
        """
        if not isinstance(path, str):
            raise TypeError(
                'path argument in %s.from_xml should be a string, not %s' %
                (self.__class__.__name__, path.__class__.__name__)
            )

        from xml.etree import ElementTree

        try:
            tree = ElementTree.parse(path)
        except IOError:
            raise IOError('Please supply a valid path to an XML file!')

        root = tree.getroot()
        seq = Sequence()
        xml_seq = root.getchildren()[0]

        seq.from_xml(xml_seq)

        # now create or update structure
        # create first
        # generate the shot name template first

        shot_name_template = self.get_shot_name_template()

        # get current sequencer
        seqs = self.sequences.get()
        if seqs:
            # we probably need to update shots
            seq1 = seqs[0]

            # update shots
            shots = seq1.shots.get()

            # collect clips
            all_clips = [clip
                         for track in seq.media.video.tracks
                         for clip in track.clips]

            deleted_shots = []

            for shot in shots:
                # find the corresponding shots in seq
                is_deleted = True
                for clip in all_clips:
                    if clip.id == shot.shotName.get():
                        # update with the given clip info
                        anchor = shot.startFrame.get()
                        handle = shot.handle.get()
                        track = shot.track.get()

                        start_frame = clip.in_ - handle + anchor
                        end_frame = clip.out - clip.in_ + start_frame

                        sequence_start = clip.start
                        sequence_end = clip.end

                        shot.startFrame.set(start_frame)
                        shot.endFrame.set(end_frame)

                        shot.sequenceStartFrame.set(sequence_start)
                        shot.sequenceEndFrame.set(sequence_end)

                        # set original track
                        shot.track.set(track)
                        is_deleted = False
                        break

                if is_deleted:
                    deleted_shots.append(shot)

            # delete shots
            pymel.core.delete(deleted_shots)

        else:
            # create sequencer
            seq1 = self.create_sequence(seq.name)

            # create shots
            media = seq.media
            for i, track in enumerate(media.video.tracks):
                for clip in track.clips:
                    shot = seq1.create_shot(clip.id)
                    shot.startFrame.set(clip.in_)
                    shot.endFrame.set(clip.out - 1)
                    shot.sequenceStartFrame.set(clip.start)
                    shot.handle.set(0)
                    if clip.file:
                        f = clip.file
                        shot.output.set(f.pathurl.replace('file://', ''))
                    shot.track.set(i + 1)

    @extends(pymel.core.nodetypes.SequenceManager)
    def to_xml(self, path=None, indentation=2, pre_indent=0):
        """Generates an FCP compatible XML file at given path.

        :param path: The path of the XML file

        :return:
        """
        seq = self.generate_sequence_structure()
        template = """<xmeml version="1.0">\n%(sequence)s\n</xmeml>\n"""

        rendered_template = ''
        if seq:
            rendered_template = template % {
                'sequence': seq.to_xml(indentation=indentation,
                                       pre_indent=indentation + pre_indent)
            }
        return rendered_template

    @extends(pymel.core.nodetypes.SequenceManager)
    def generate_sequence_structure(self):
        """Generates a Sequence structure suitable for XML<->EDL conversion

        :return: Sequence
        """
        import pytimecode
        from anima.pipeline.env import maya
        mayaEnv = maya.Maya()
        fps = mayaEnv.get_fps()

        # export only the first sequence, ignore others
        sequencers = self.sequences.get()
        if len(sequencers) == 0:
            return None

        sequencer = sequencers[0]
        time = pymel.core.PyNode('time1')

        seq = Sequence()
        seq.name = str(sequencer.get_sequence_name())
        seq.ntsc = False  # always false

        seq.timebase = str(fps)
        seq.timecode = str(pytimecode.PyTimeCode(
            framerate=seq.timebase,
            frames=time.timecodeProductionStart.get() + 1
        ))
        seq.duration = sequencer.duration

        media = Media()
        video = Video()
        media.video = video

        for shot in sequencer.shots.get():
            clip = Clip()
            clip.id = str(shot.shotName.get())
            clip.name = str(shot.full_shot_name)
            clip.duration = shot.duration + 2 * shot.handle.get()
            clip.enabled = True
            clip.start = shot.sequenceStartFrame.get()
            clip.end = shot.sequenceEndFrame.get() + 1
            # clips always start from 0 and includes the shot handle
            clip.in_ = shot.handle.get()  # handle at start
            clip.out = shot.handle.get() + shot.duration  # handle at end
            clip.type = 'Video'  # always video for now

            file = File()
            file.name = os.path.splitext(
                os.path.basename(str(shot.output.get()))
            )[0]

            file.duration = shot.duration + 2 * shot.handle.get()

            file.pathurl = str('file://%s' % shot.output.get())

            clip.file = file

            track_number = shot.track.get() - 1  # tracks should start from 0
            try:
                track = video.tracks[track_number]
            except IndexError:
                track = Track()
                video.tracks.append(track)

            track.clips.append(clip)
            # set video resolution
            video.width = shot.wResolution.get()
            video.height = shot.hResolution.get()

        seq.media = media
        return seq

    @extends(pymel.core.nodetypes.SequenceManager)
    def to_edl(self):
        """Generates an EDL file out of the edit
        """
        seq = self.generate_sequence_structure()
        l = seq.to_edl()
        return l


class SequencerExtension(object):
    """The sequence instance.

    It is a manager that manages shot data. It is kind of the reflection of the
    Maya Sequencer instance.

    It is able to get Maya editorial XML and convert it to EDL.
    """

    @extends(pymel.core.nodetypes.Sequencer)
    @property
    def manager(self):
        """returns the SequenceManager instance that this sequence is connected
        to
        """
        return self.message.get()

    @extends(pymel.core.nodetypes.Sequencer)
    def get_sequence_name(self):
        """Gets the sequence_name attribute value, creates the attribute if it
        is missing
        """
        if not self.hasAttr('sequence_name'):
            self.set_sequence_name('')
        return self.sequence_name.get()

    @extends(pymel.core.nodetypes.Sequencer)
    def set_sequence_name(self, name):
        """Sets the sequence name for this Sequencer

        :param name: A str holding the desired name of the sequence.
        :return: None
        """
        if not self.hasAttr('sequence_name'):
            self.addAttr('sequence_name', dt='string')
        self.sequence_name.set(name)

    @extends(pymel.core.nodetypes.Sequencer)
    @property
    def all_shots(self):
        """return all the shots connected to this sequencer
        """
        return self.shots.get()

    # @extends(pymel.core.nodetypes.Sequencer)
    # @all_shots.setter
    # def all_shots(self, shots):
    #     """setter for the all_shots property
    #     """
    #     # remove the current shots first
    #     # then append the new ones
    #     for s in self.all_shots:
    #         t = s // self.shots
    #
    #     for s in shots:
    #         t = s.message >> self.shots.next_available

    @extends(pymel.core.nodetypes.Sequencer)
    def add_shot(self, shot):
        """Adds the given shot to the current sequencer

        :param shot: a pymel.core.nodetypes.Shot instance
        :return: None
        """
        # add the given shot to the list
        if not shot.hasAttr('handle'):
            shot.set_handle(handle=10)

        # connect to the sequencer
        # remove it from other sequences
        for attr in shot.message.outputs(p=1):
            if isinstance(attr.node(), pymel.core.nodetypes.Sequencer):
                shot.message // attr

        shot.message >> self.shots.next_available

    @extends(pymel.core.nodetypes.Sequencer)
    def set_shot_handles(self, handle=10):
        """Set shot handles

        :param int handle: An integer value for handle
        :return:
        """
        # validate arguments
        # shots
        for shot in self.all_shots:
            shot.set_handle(handle)

    @extends(pymel.core.nodetypes.Sequencer)
    def mute_shots(self):
        """mutes all shots connected to this sequencer
        """
        for shot in self.all_shots:
            shot.mute()

    @extends(pymel.core.nodetypes.Sequencer)
    def unmute_shots(self):
        """unmutes all shots connected to this sequencer
        """
        for shot in self.all_shots:
            shot.unmute()

    def create_sequencer_attributes(self):
        """Creates the necessary extra attributes for the sequencer in the
        current scene.

        Add attributes like:
            sequenceName
            shotNameTemplate
            defaultHandle
        """
        raise NotImplementedError()

    def set_shot_names(self, sequence_name, padding=4, increment=10,
                       template='%(sequence_name)s_%(shot_name)_%(version_number)03d'):
        """Sets all shot names according to the given template.

        :param sequence_name: The sequence name
        :param padding: Shot number padding
        :param increment: Shot number increment
        :param template: The final shot name template
        :return:
        """
        raise NotImplementedError()

    @extends(pymel.core.nodetypes.Sequencer)
    def create_shot(self, name='', handle=10):
        """Creates a new shot.

        :param str name: A string value for the newly created shot name, if
          skipped or given empty, the next empty shot name will be generated.
        :param int handle: An integer value for the handle attribute. Default
          is 10.
        :returns: The created :class:`~pymel.core.nt.Shot` instance
        """
        shot = pymel.core.createNode('shot')
        shot.shotName.set(name)
        shot.set_handle(handle=handle)
        shot.set_output('')

        # connect to the sequencer
        shot.message >> self.shots.next_available
        return shot

    @extends(pymel.core.nodetypes.Sequencer)
    def create_shot_playblasts(self, output_path, show_ornaments=True):
        """creates the selected shot playblasts
        """
        movie_files = []
        for shot in self.shots.get():
            movie_files.append(
                shot.playblast(output_path, show_ornaments=show_ornaments)
            )
        return movie_files

    @extends(pymel.core.nodetypes.Sequencer)
    def to_edl(self, seq):
        """returns an EDL for the given sequence

        :param seq: A :class:`.Sequence` instance
        """
        return seq.to_edl()

    @extends(pymel.core.nodetypes.Sequencer)
    def metafuze(self, xml):
        """Calls "Avid Metafuze" with the given xml content to convert media
        files to MXF format.

        :param str xml: The xml content
        :return:
        """
        # write the given content to tmp
        temp_file_path = tempfile.mktemp()
        with open(temp_file_path, 'w') as f:
            f.write(xml)

        process = subprocess.Popen(
            ['metafuze',
             temp_file_path],
            stderr=subprocess.PIPE
        )
        # wait it to complete
        process.wait()

        stderr = process.stderr.readlines()

        if process.returncode:
            # there is an error
            raise RuntimeError(stderr)

        # remove the temp file
        os.remove(temp_file_path)

    @extends(pymel.core.nodetypes.Sequencer)
    def convert_to_mxf(self, path):
        """converts the given video at given path to Avid MXF DNxHD 36.

        :param path: The path of the media file
        :return: returns the generated mxf file location
        """
        raise NotImplementedError()

    @extends(pymel.core.nodetypes.Sequencer)
    @property
    def duration(self):
        """returns the duration of this sequence
        """
        return self.maxFrame.get() - self.minFrame.get() + 1


class ShotExtension(object):
    """extensions to pymel.core.nodetypes.Shot class
    """

    @extends(pymel.core.nodetypes.Shot)
    def get_output(self):
        """Gets the output attribute value of this shot, creates the attribute
        if it is missing
        """
        if not self.hasAttr('output'):
            self.set_output('')
        return self.output.get()

    @extends(pymel.core.nodetypes.Shot)
    def set_output(self, output):
        """Sets the output of this shot. The output is generally a movie file
        automatically created by calling shot.playblast() method.

        :param str output: A string value showing the path of this shots
          output.
        :return:
        """
        if not self.hasAttr('output'):
            self.addAttr('output', dt='string')
        self.output.set(output)

    @extends(pymel.core.nodetypes.Shot)
    def mute(self):
        """Mutes the current shot

        :param mode: True to mute False to unmute
        :return:
        """
        pymel.core.shot(self, e=1, mute=True)

    @extends(pymel.core.nodetypes.Shot)
    def unmute(self):
        """Unmutes the current shot.

        :return:
        """
        pymel.core.shot(self, e=1, mute=False)

    @extends(pymel.core.nodetypes.Shot)
    @property
    def sequence(self):
        """returns the current sequencer
        """
        return self.message.get()

    @extends(pymel.core.nodetypes.Shot)
    @property
    @contextmanager
    def include_handles(self):
        """includes the handle values to the shot range, primarily done for
        taking playblasts with handles
        """
        handle = self.handle.get()
        track = self.track.get()
        self.startFrame.set(
            self.startFrame.get() - handle
        )
        self.endFrame.set(
            self.endFrame.get() + handle
        )
        self.sequenceStartFrame.set(
            self.sequenceStartFrame.get() - handle
        )
        try:
            yield None
        finally:
            self.startFrame.set(
                self.startFrame.get() + handle
            )
            self.endFrame.set(
                self.endFrame.get() - handle
            )
            self.sequenceStartFrame.set(
                self.sequenceStartFrame.get() + handle
            )
            self.track.set(track)

    @extends(pymel.core.nodetypes.Shot)
    def playblast(self, output_path, show_ornaments=True):
        """creates the selected shot playblasts
        """
        # TODO: create test for this (how??? no OpenGL)
        # get current version and then the output folder
        path_template = os.path.join(output_path).replace('\\', '/')

        filename_template = '%(sequence)s_%(shot)s.mov'

        # template vars
        sequence = self.sequence

        sequence_name = sequence.sequence_name.get()
        shot_name = self.shotName.get()
        handle = self.handle.get()
        start_frame = self.sequenceStartFrame.get() - handle
        end_frame = self.sequenceEndFrame.get() + handle
        width = self.wResolution.get()
        height = self.hResolution.get()

        # store track
        track = self.track.get()

        rendered_path = path_template % {}
        rendered_filename = filename_template % {
            'shot': shot_name,
            'sequence': sequence_name
        }

        movie_full_path = os.path.join(
            rendered_path,
            rendered_filename
        ).replace('\\', '/')

        # set the output of this shot
        self.set_output(movie_full_path)

        # mute all other shots
        sequence.mute_shots()
        self.unmute()

        # include handles
        with self.include_handles:
            pymel.core.system.dgdirty(a=True)

            result = pymel.core.playblast(
                fmt="qt",
                startTime=start_frame,
                endTime=end_frame,
                sequenceTime=1,
                forceOverwrite=1,
                filename=movie_full_path,
                clearCache=True,
                showOrnaments=show_ornaments,
                percent=100,
                wh=[width, height],
                offScreen=True,
                viewer=0,
                useTraxSounds=True,
                compression="PNG",
                quality=70
            )
            sequence.unmute_shots()

        # restore track
        self.track.set(track)

        return result

    @extends(pymel.core.nodetypes.Shot)
    def convert_to_mxf(self):
        """converts the given video at given path to Avid MXF DNxHD 36.

        :return: returns the generated mxf file location
        """
        pass

    @extends(pymel.core.nodetypes.Shot)
    def set_handle(self, handle=10):
        """Creates handle attribute to given shot instance

        :param int handle: An integer value for handle
        :return:
        """
        if not isinstance(handle, int):
            raise TypeError(
                '"handle" argument in %(class)s.set_handle() should be '
                'a non negative integer, not %(handle_class)s' %
                {
                    'class': self.__class__.__name__,
                    'handle_class': handle.__class__.__name__
                }
            )

        if handle < 0:
            raise ValueError(
                '"handle" argument in %(class)s.set_handle() should be '
                'a non negative integer, not %(handle)s' %
                {
                    'class': self.__class__.__name__,
                    'handle': handle
                }
            )

        # create "handle" attribute in each shot and set the value
        try:
            self.addAttr('handle', at='short', k=True, min=0)
        except RuntimeError:
            # attribute is already there
            pass
        self.setAttr('handle', handle)

    @extends(pymel.core.nodetypes.Shot)
    @property
    def duration(self):
        """returns the shot duration
        """
        return self.sequenceEndFrame.get() - self.sequenceStartFrame.get() + 1

    def add_frames_to_start(self, shot, frame_count=0):
        """Adds extra frames to the given shots start, and offsets all the
        following shots with the given frame_count.

        :param shot: A :class:`~pymel.core.nt.Shot` instance.
        :param int frame_count: The frame count to be added
        :return:
        """
        pass

    def add_frames_to_end(self, shot, frame_count=0):
        """Adds extra frames to the given shot, and offsets all the following
        shots with the given frame_count.

        :param shot: A :class:`~pymel.core.nt.Shot` instance.
        :param int frame_count: The frame count to be added
        :return:
        """
        pass

    def remove_frames_from_start(self, shot, frame_count=0):
        """Removes frames from the given shots beginning, and offsets all the
        following shots back with the given frame_count.

        :param shot: A :class:`~pymel.core.nt.Shot` instance.
        :param int frame_count: The frame count to be added
        :return:
        """
        pass

    def remove_frames_from_end(self, shot, frame_count=0):
        """Removes frames from the given shots end, and offsets all the
        following shots back with the given frame_count.

        :param shot: A :class:`~pymel.core.nt.Shot` instance.
        :param int frame_count: The frame count to be added
        :return:
        """
        pass

    @extends(pymel.core.nodetypes.Shot)
    @property
    def full_shot_name(self):
        """returns the full shot name
        """
        seq = self.sequence
        sm = seq.manager
        camera = self.currentCamera.get()
        version = sm.get_version()
        template = sm.get_shot_name_template()

        # replace template variables
        template = template\
            .replace('<Sequence>', '%(sequence)s')\
            .replace('<Shot>', '%(shot)s')\
            .replace('<Version>', '%(version)s')\
            .replace('<Camera>', '%(camera)s')

        rendered_template = template % {
            'shot': self.shotName.get(),
            'sequence': seq.sequence_name.get(),
            'version': version,
            'camera': camera.name.get() if camera else None
        }

        return rendered_template


class Sequence(PrevisBase, NameMixin, DurationMixin):
    """XML compatibility class for Sequence

    This class is mainly created to reflect the XML structure of Maya
    Sequencer.

    It is also the bridge to EDL. So using this class it is possible to convert
    Maya Sequencer XML to a meaningful EDL.

    :param str name: The name of this sequence.
    :param float duration: The duration of this sequence.
    :param str timebase: The frame rate setting for this sequence. Default
      value is '25', can be anything in ['23.98', '24', '25', '29.97', '30',
      '50', '59.94', '60']. Without setting this converting to EDL will result
      wrong timecode values in EDL.
    :param str timecode: The stating timecode of this Sequence. Default value
      is '00:00:00:00'. This will be used to calculate the clip in and out
      points. Maya exports in and out points as frames, Sequence converts them
      to a timecodes by using this parameter as the base.
    """

    def __init__(self, name='', duration=0.0, timebase='25',
                 timecode='00:00:00:00'):
        NameMixin.__init__(self, name=name)
        DurationMixin.__init__(self, duration=duration)
        self.ntsc = False
        # replace this with pytimecode.PyTimeCode instance
        self.timecode = timecode
        self.timebase = timebase
        self.media = None

    def from_xml(self, xml_node):
        """Fills attributes with the given XML node

        :param xml_node: an xml.etree.ElementTree.Element instance
        """
        self.duration = float(xml_node.find('duration').text)
        self.name = xml_node.find('name').text
        rate_tag = xml_node.find('rate')
        if rate_tag is not None:
            self.ntsc = rate_tag.find('ntsc').text.title() == 'True'
            self.timebase = rate_tag.find('timebase').text

        self.timecode = xml_node.find('timecode').find('string').text

        xml_media = xml_node.find('media')
        media = Media()
        media.from_xml(xml_media)

        self.media = media

    def to_xml(self, indentation=2, pre_indent=0):
        """returns an xml version of this Sequence object
        """
        template = """%(pre_indent)s<sequence>
%(pre_indent)s%(indentation)s<duration>%(duration)s</duration>
%(pre_indent)s%(indentation)s<name>%(name)s</name>
%(pre_indent)s%(indentation)s<rate>
%(pre_indent)s%(indentation)s%(indentation)s<ntsc>%(ntsc)s</ntsc>
%(pre_indent)s%(indentation)s%(indentation)s<timebase>%(timebase)s</timebase>
%(pre_indent)s%(indentation)s</rate>
%(pre_indent)s%(indentation)s<timecode>
%(pre_indent)s%(indentation)s%(indentation)s<string>%(timecode)s</string>
%(pre_indent)s%(indentation)s</timecode>
%(media)s
%(pre_indent)s</sequence>"""

        return template % {
            'duration': self.duration,
            'name': self.name,
            'ntsc': str(self.ntsc).upper(),
            'timebase': self.timebase,
            'timecode': self.timecode,
            'media': self.media.to_xml(indentation=indentation,
                                       pre_indent=indentation + pre_indent),
            'indentation': ' ' * indentation,
            'pre_indent': ' ' * pre_indent
        }

    def from_edl(self, edl_list):
        """Fills attributes with the given edl.List instance

        :param edl_list: an edl.List instance
        """
        import edl
        assert isinstance(edl_list, edl.List)

        self.name = edl_list.title

        # create a Media instance
        self.media = Media()

        v = Video()
        self.media.video = v

        video_track = Track()
        v.tracks.append(video_track)
        # no audio tracks fow now

        # read Events in to Clips
        sequence_start = 1e20
        sequence_end = -1
        for e in edl_list.events:
            assert isinstance(e, edl.Event)
            clip = Clip()

            clip.name = e.clip_name
            clip.id = e.reel
            clip.type = 'Video' if e.track == 'V' else 'Audio'

            clip.in_ = e.src_start_tc.frame_number
            clip.out = e.src_end_tc.frame_number
            clip.duration = clip.out  # including the handle at start,
                                      # but we can not have any idea about the
                                      # handle at end

            clip.start = e.rec_start_tc.frame_number
            clip.end = e.rec_end_tc.frame_number

            if clip.start < sequence_start:
                sequence_start = clip.start
            if clip.end > sequence_end:
                sequence_end = clip.end

            f = File()
            f.name = clip.name
            f.duration = clip.duration
            f.pathurl = 'file://%s' % e.source_file

            clip.file = f

            if clip.type == 'Video':
                video_track.clips.append(clip)

        self.duration = sequence_end - sequence_start
        # TODO: fix this latest, timecode always 00:00:00:00 for now
        self.timecode = '00:00:00:00'
        # TODO: can not read sequence.timebase from edl

    def to_edl(self):
        """Returns an edl.List instance equivalent of this Sequence instance
        """
        from edl import List, Event
        from pytimecode import PyTimeCode

        l = List(self.timebase)
        l.title = self.name

        # convert clips to events
        if not self.media:
            raise RuntimeError(
                'Can not run %(class)s.to_edl() without a Media instance, '
                'please add a Media instance to this %(class)s instance.' % {
                    'class': self.__class__.__name__
                }
            )

        video = self.media.video
        if video is not None:
            i = 0
            for track in video.tracks:
                for clip in track.clips:
                    i += 1
                    e = Event({})
                    e.num = '%06i' % i
                    e.clip_name = clip.name
                    e.reel = clip.id
                    e.track = 'V' if clip.type == 'Video' else 'A'
                    e.tr_code = 'C'  # TODO: for now use C (Cut) later on
                    # expand it to add other transition codes

                    src_start_tc = PyTimeCode(self.timebase,
                                              frames=clip.in_ + 1)
                    # 1 frame after last frame shown
                    src_end_tc = PyTimeCode(self.timebase,
                                            frames=clip.out + 1)

                    e.src_start_tc = str(src_start_tc)
                    e.src_end_tc = str(src_end_tc)

                    rec_start_tc = PyTimeCode(self.timebase,
                                              frames=clip.start + 1)
                    # 1 frame after last frame shown
                    rec_end_tc = PyTimeCode(self.timebase, frames=clip.end + 1)

                    e.rec_start_tc = str(rec_start_tc)
                    e.rec_end_tc = str(rec_end_tc)

                    source_file = clip.file.pathurl.replace('file://', '')
                    e.source_file = source_file

                    e.comments.extend([
                        '* FROM CLIP NAME: %s' % clip.name,
                        '* SOURCE FILE: %s' % source_file
                    ])

                    l.append(e)
        return l

    def to_metafuze_xml(self):
        """Generates a MetaFuze compatible XML content per clip.

        :returns: list of strings
        """
        metafuze_xml_template = """<?xml version='1.0' encoding='UTF-8'?>
<MetaFuze_BatchTranscode>
   <Configuration>
      <Local>8</Local>
      <Remote>8</Remote>
   </Configuration>
   <Group>
      <FileList>
         <File>%(file_pathurl)s</File>
      </FileList>
      <Transcode>
         <Version>1.0</Version>
         <File>%(mxf_pathurl)s</File>
         <ClipName>%(clip_name)s</ClipName>
         <ProjectName>%(sequence_name)s</ProjectName>
         <TapeName>%(clip_name)s</TapeName>
         <TC_Start>%(sequence_timecode)s</TC_Start>
         <DropFrame>false</DropFrame>
         <EdgeTC>** TimeCode N/A **</EdgeTC>
         <FilmType>35.4</FilmType>
         <KN_Start>AAAAAAAA-0000+00</KN_Start>
         <Frames>%(clip_duration)i</Frames>
         <Width>%(width)i</Width>
         <Height>%(height)i</Height>
         <PixelRatio>1.0000</PixelRatio>
         <UseFilmInfo>false</UseFilmInfo>
         <UseTapeInfo>true</UseTapeInfo>
         <AudioChannelCount>0</AudioChannelCount>
         <UseMXFAudio>false</UseMXFAudio>
         <UseWAVAudio>false</UseWAVAudio>
         <SrcBitsPerChannel>8</SrcBitsPerChannel>
         <OutputPreset>DNxHD 36 - 1080 24p (8 bits)</OutputPreset>
         <OutputPreset>
            <Version>2.0</Version>
            <Name>DNxHD 36 - 1080 24p (8 bits)</Name>
            <ColorModel>YCC 709</ColorModel>
            <BitDepth>8</BitDepth>
            <Format>1080 24p</Format>
            <Compression>DNxHD 36</Compression>
            <Conversion>Letterbox (center)</Conversion>
            <VideoFileType>.mxf</VideoFileType>
            <IsDefault>false</IsDefault>
         </OutputPreset>
         <Eye></Eye>
         <Scene></Scene>
         <Comment></Comment>
      </Transcode>
   </Group>
</MetaFuze_BatchTranscode>"""
        rendered_xmls = []
        video = self.media.video
        if video is not None:
            for track in video.tracks:
                for clip in track.clips:
                    raw_file_path = clip.file.pathurl.replace('file://', '')
                    raw_mxf_path = '%s%s' % (
                        os.path.splitext(raw_file_path)[0],
                        '.mxf'
                    )

                    kwargs = {
                        'file_pathurl': raw_file_path,
                        'mxf_pathurl': raw_mxf_path,
                        'sequence_name': self.name,
                        'sequence_timecode': self.timecode,
                        'clip_id': clip.id,
                        'clip_name': clip.name,
                        'clip_duration': clip.duration,
                        'width': video.width,
                        'height': video.height
                    }

                    rendered_xmls.append(metafuze_xml_template % kwargs)

        return rendered_xmls


class Media(PrevisBase):
    """XML compatibility class for Sequencer
    """

    def __init__(self):
        self.video = None
        self.audio = None

    def from_xml(self, xml_node):
        """Fills attributes with the given XML node

        :param xml_node: an xml.etree.ElementTree.Element instance
        """
        xml_video_tag = xml_node.find('video')
        video = Video()
        video.from_xml(xml_video_tag)
        self.video = video

    def to_xml(self, indentation=2, pre_indent=0):
        """returns an xml version of this Media object
        """
        template = """%(pre_indent)s<media>
%(video)s
%(pre_indent)s</media>"""

        video_data = self.video.to_xml(
            indentation=indentation,
            pre_indent=indentation + pre_indent
        )

        return template % {
            'video': video_data,
            'pre_indent': ' ' * pre_indent,
            'indentation': ' ' * indentation
        }


class Video(PrevisBase):
    """XML compatibility class for Sequencer
    """

    def __init__(self):
        self.width = 0
        self.height = 0
        self.tracks = []

    def from_xml(self, xml_node):
        """Fills attributes with the given XML node

        :param xml_node: an xml.etree.ElementTree.Element instance
        """
        format_node = xml_node.find('format')
        self.width = int(
            format_node.find('samplecharacteristics').find('width').text
        )
        self.height = int(
            format_node.find('samplecharacteristics').find('height').text
        )

        # create tracks
        track_tag = xml_node.find('track')
        track = Track()
        track.from_xml(track_tag)

        self.tracks.append(track)

    def to_xml(self, indentation=2, pre_indent=0):
        """returns an xml version of this Video object
        """
        template = """%(pre_indent)s<video>
%(pre_indent)s%(indentation)s<format>
%(pre_indent)s%(indentation)s%(indentation)s<samplecharacteristics>
%(pre_indent)s%(indentation)s%(indentation)s%(indentation)s<width>%(width)s</width>
%(pre_indent)s%(indentation)s%(indentation)s%(indentation)s<height>%(height)s</height>
%(pre_indent)s%(indentation)s%(indentation)s</samplecharacteristics>
%(pre_indent)s%(indentation)s</format>
%(tracks)s
%(pre_indent)s</video>"""

        track_data = []
        for track in self.tracks:
            track_data.append(
                track.to_xml(indentation=indentation,
                             pre_indent=indentation + pre_indent)
            )
        track_data_as_str = '\n'.join(track_data)

        return template % {
            'width': self.width,
            'height': self.height,
            'tracks': track_data_as_str,
            'pre_indent': ' ' * pre_indent,
            'indentation': ' ' * indentation
        }


class Track(PrevisBase):
    """XML compatibility class for Sequencer
    """

    def __init__(self):
        self.locked = False
        self.enabled = True
        self.clips = []

    def from_xml(self, xml_node):
        """Fills attributes with the given XML node

        :param xml_node: an xml.etree.ElementTree.Element instance
        """
        self.locked = xml_node.find('locked').text.title() == 'True'
        self.enabled = xml_node.find('enabled').text.title() == 'True'

        # find clips
        for clip_tag in xml_node.findall('clipitem'):
            clip = Clip()
            clip.from_xml(clip_tag)
            self.clips.append(clip)

    def to_xml(self, indentation=2, pre_indent=0):
        """returns an xml version of this Track object
        """
        template = """%(pre_indent)s<track>
%(pre_indent)s%(indentation)s<locked>%(locked)s</locked>
%(pre_indent)s%(indentation)s<enabled>%(enabled)s</enabled>
%(clips)s
%(pre_indent)s</track>"""

        clip_data = []
        for clip in self.clips:
            clip_data.append(
                clip.to_xml(indentation=indentation,
                            pre_indent=indentation + pre_indent)
            )
        clip_data_as_str = '\n'.join(clip_data)

        return template % {
            'locked': str(self.locked).upper(),
            'enabled': str(self.enabled).upper(),
            'clips': clip_data_as_str,
            'pre_indent': ' ' * pre_indent,
            'indentation': ' ' * indentation
        }


class Clip(PrevisBase, NameMixin, DurationMixin):
    """XML compatibility class for Sequencer
    """

    def __init__(self, id=None, name='', start=0.0, end=0.0, duration=0.0,
                 enabled=True, in_=0, out=0, type_='Video'):
        NameMixin.__init__(self, name=name)
        DurationMixin.__init__(self, duration=duration)
        self._id = self._validate_id(id)
        self.start = start
        self.end = end
        self.enabled = enabled
        self.in_ = in_
        self.out = out
        self.file = None
        self.type = type_

    @classmethod
    def _validate_id(cls, id_):
        """validates the given id value
        """
        if id_ is None:
            id_ = ''

        if not isinstance(id_, str):
            raise TypeError(
                '%(class)s.id should be a string, not %(id_class)s' %
                {
                    'class': cls.__name__,
                    'id_class': id_.__class__.__name__
                }
            )

        return id_

    @property
    def id(self):
        """returns the _id attribute value
        """
        return self._id

    @id.setter
    def id(self, id_):
        """setter for the _id attribute
        """
        self._id = self._validate_id(id_)

    def from_xml(self, xml_node):
        """Fills attributes with the given XML node

        :param xml_node: an xml.etree.ElementTree.Element instance
        """
        self.id = xml_node.attrib['id']
        self.start = float(xml_node.find('start').text)
        self.end = float(xml_node.find('end').text)
        self.name = xml_node.find('name').text
        self.enabled = xml_node.find('enabled').text == 'True'
        self.duration = float(xml_node.find('duration').text)
        self.in_ = float(xml_node.find('in').text)
        self.out = float(xml_node.find('out').text)

        f = File()
        file_tag = xml_node.find('file')
        f.from_xml(file_tag)

        self.file = f

    def to_xml(self, indentation=2, pre_indent=0):
        """returns an xml version of this Clip object
        """
        template = """%(pre_indent)s<clipitem id="%(id)s">
%(pre_indent)s%(indentation)s<end>%(end)1.1f</end>
%(pre_indent)s%(indentation)s<name>%(name)s</name>
%(pre_indent)s%(indentation)s<enabled>%(enabled)s</enabled>
%(pre_indent)s%(indentation)s<start>%(start)1.1f</start>
%(pre_indent)s%(indentation)s<in>%(in)1.1f</in>
%(pre_indent)s%(indentation)s<duration>%(duration)1.1f</duration>
%(pre_indent)s%(indentation)s<out>%(out)1.1f</out>
%(file)s
%(pre_indent)s</clipitem>"""

        return template % {
            'id': self.id,
            'start': self.start,
            'end': self.end,
            'name': self.name,
            'enabled': self.enabled,
            'duration': self.duration,
            'in': self.in_,
            'out': self.out,
            'file': self.file.to_xml(indentation=indentation,
                                     pre_indent=pre_indent + indentation),
            'pre_indent': ' ' * pre_indent,
            'indentation': ' ' * indentation
        }


class File(PrevisBase, NameMixin, DurationMixin):
    """XML compatibility class for Sequencer
    """

    def __init__(self, duration=0, name='', pathurl=''):
        NameMixin.__init__(self, name=name)
        DurationMixin.__init__(self, duration=duration)
        self._pathurl = self._validate_pathurl(pathurl)

    @classmethod
    def _validate_pathurl(cls, pathurl):
        """validates the given pathurl value
        """
        if not isinstance(pathurl, str):
            raise TypeError(
                '%(class)s.pathurl should be a string, not '
                '%(pathurl_class)s' % {
                    'class': cls.__name__,
                    'pathurl_class': pathurl.__class__.__name__
                }
            )
        return pathurl

    @property
    def pathurl(self):
        """returns the _pathurl attribute
        """
        return self._pathurl

    @pathurl.setter
    def pathurl(self, pathurl):
        """setter for the pathurl property
        """
        self._pathurl = self._validate_pathurl(pathurl)

    def from_xml(self, xml_node):
        """Fills attributes with the given XML node

        :param xml_node: an xml.etree.ElementTree.Element instance
        """
        duration_node = xml_node.find('duration')
        if duration_node is not None:
            self.duration = float(duration_node.text)

        name_node = xml_node.find('name')
        if name_node is not None:
            self.name = name_node.text

        pathurl_node = xml_node.find('pathurl')
        if pathurl_node is not None:
            self.pathurl = pathurl_node.text

    def to_xml(self, indentation=2, pre_indent=0):
        """returns an xml version of this File object
        """
        template = """%(pre_indent)s<file>
%(pre_indent)s%(indentation)s<duration>%(duration)s</duration>
%(pre_indent)s%(indentation)s<name>%(name)s</name>
%(pre_indent)s%(indentation)s<pathurl>%(pathurl)s</pathurl>
%(pre_indent)s</file>"""
        return template % {
            'duration': self.duration,
            'name': self.name,
            'pathurl': self.pathurl,
            'pre_indent': ' ' * pre_indent,
            'indentation': ' ' * indentation
        }

