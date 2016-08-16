#   Copyright (c) 2016, Xilinx, Inc.
#   All rights reserved.
# 
#   Redistribution and use in source and binary forms, with or without 
#   modification, are permitted provided that the following conditions are met:
#
#   1.  Redistributions of source code must retain the above copyright notice, 
#       this list of conditions and the following disclaimer.
#
#   2.  Redistributions in binary form must reproduce the above copyright 
#       notice, this list of conditions and the following disclaimer in the 
#       documentation and/or other materials provided with the distribution.
#
#   3.  Neither the name of the copyright holder nor the names of its 
#       contributors may be used to endorse or promote products derived from 
#       this software without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
#   THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
#   PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
#   EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
#   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#   OR BUSINESS INTERRUPTION). HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
#   WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
#   OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
#   ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

__author__ = "Giuseppe Natale, Yun Rock Qu"
__copyright__ = "Copyright 2016, Xilinx"
__email__ = "pynq_support@xilinx.com"

from pynq import PL
from time import sleep
from itertools import chain
from PIL import Image
from . import _video

VDMA_DICT = {
    'BASEADDR': 0x43000000,
    'NUM_FSTORES': 3,
    'INCLUDE_MM2S': 1,
    'INCLUDE_MM2S_DRE': 0,
    'M_AXI_MM2S_DATA_WIDTH': 32,
    'INCLUDE_S2MM': 1,
    'INCLUDE_S2MM_DRE': 0,
    'M_AXI_S2MM_DATA_WIDTH': 32,
    'INCLUDE_SG': 0,
    'ENABLE_VIDPRMTR_READS': 1,
    'USE_FSYNC': 1,
    'FLUSH_ON_FSYNC': 1,
    'MM2S_LINEBUFFER_DEPTH': 4096,
    'S2MM_LINEBUFFER_DEPTH': 4096,
    'MM2S_GENLOCK_MODE': 0,
    'S2MM_GENLOCK_MODE': 0,
    'INCLUDE_INTERNAL_GENLOCK': 1,
    'S2MM_SOF_ENABLE': 1,
    'M_AXIS_MM2S_TDATA_WIDTH': 24,
    'S_AXIS_S2MM_TDATA_WIDTH': 24,
    'ENABLE_DEBUG_INFO_1': 0,
    'ENABLE_DEBUG_INFO_5': 0,
    'ENABLE_DEBUG_INFO_6': 1,
    'ENABLE_DEBUG_INFO_7': 1,
    'ENABLE_DEBUG_INFO_9': 0,
    'ENABLE_DEBUG_INFO_13': 0,
    'ENABLE_DEBUG_INFO_14': 1,
    'ENABLE_DEBUG_INFO_15': 1,
    'ENABLE_DEBUG_ALL': 0,
    'ADDR_WIDTH': 32,
}

VTC_DISPLAY_ADDR = int(PL.ip_dict["SEG_v_tc_0_Reg"][0],16)#0x43C20000
VTC_CAPTURE_ADDR = int(PL.ip_dict["SEG_v_tc_1_Reg"][0],16)#0x43C30000
DYN_CLK_ADDR = int(PL.ip_dict["SEG_axi_dynclk_0_reg0"][0],16)#0x43C10000

GPIO_DICT = {
    'BASEADDR': 0x41220000,
    'INTERRUPT_PRESENT': 1,
    'IS_DUAL': 1,
}

MAX_FRAME_WIDTH = 1920
MAX_FRAME_HEIGHT = 1080

class HDMI(object):
    """Class for an HDMI controller.

    The frame buffer in an HDMI object can be shared among different objects.
    e.g., a VGA object and an HDMI object can use the same frame buffer.
    
    Note
    ----
    HDMI supports direction 'in' and 'out'.
    
    Examples
    --------
    >>> hdmi = HDMI('in')
    >>> hdmi = HDMI('out')
    
    Attributes
    ----------
    direction : str
        Can be 'in' for HDMI to be input or 'out' for HDMI to be output.
    frame_buffer : _framebuffer
        A frame buffer storing at most 3 frames.
        
    Raises
    ------
    ValueError
        
    """

    def __init__(self, direction, frame_buffer=None):
        """Returns a new instance of an HDMI object. 
        
        Assign the given frame buffer if specified, otherwise create a new 
        frame buffer.
        
        Note
        ----
        HDMI supports direction 'in' and 'out'.
        
        Parameters
        ----------
        direction : str
        frame_buffer : optional[_framebuffer] 
            A frame buffer storing at most 3 frames.
        
        """
        if not direction.lower() == 'in':
            self.direction = 'out'
            if frame_buffer == None:
                self._display = _video._display(VDMA_DICT,
                                                VTC_DISPLAY_ADDR,
                                                DYN_CLK_ADDR, 1)
            else:
                self._display = _video._display(VDMA_DICT,
                                                VTC_DISPLAY_ADDR,
                                                DYN_CLK_ADDR, 1,
                                                frame_buffer)
                                                
            self.frame_buffer = self._display.framebuffer
            
            self.start = self._display.start
            """Start the video controller.
            
            Parameters
            ----------
            None
            
            Returns
            -------
            None
            
            """

            self.stop = self._display.stop
            """Stop the video controller.
            
            Parameters
            ----------
            None
            
            Returns
            -------
            None
            
            """

            self.state = self._display.state
            """Get the state of the device as an integer value.
            
            Parameters
            ----------
            None
            
            Returns
            -------
            int
                The state 0 (STOPPED), or 1 (RUNNING).
                
            """

            self.mode = self._display.mode
            """Change the resolution of the display. 
            
            Users can use mode(new_mode) to change the resolution.
            Specifically, with `new_mode` to be:
            0 : '640x480@60Hz'
            1 : '800x600@60Hz'
            2 : '1280x720@60Hz'
            3 : '1280x1024@60Hz'
            4 : '1920x1080@60Hz'           
            
            If `new_mode` is not specified, return the current mode.

            Parameters
            ----------
            new_mode : int
                A mode index from 0 to 4.
                
            Returns
            -------
            str
                The resolution of the VGA display.
                
            Raises
            ------
            ValueError
                If `new_mode` is out of range.
                
            """

            self.frame_raw = self._display.frame
            """Returns a bytearray of the frame.
            
            User may use frame([index]) to access the frame, which may 
            introduce some overhead in rare cases. The method 
            frame_raw([i],[new_frame]) is faster, but the parameter `i` has 
            to be calculated manually.

            Note
            ----
            If `new_frame` is set, this method will take the bytearray 
            (`new_frame`) and overwrites the current frame (or the frame 
            specified by `i`). Also, if `new_frame` is set, nothing will 
            be returned.
            
            Parameters
            ----------
            i : optional[int]
                A location in the bytearray.
            new_frame: optional[bytearray]
                A bytearray that can be used to overwrite the frame.
                
            Returns
            -------
            bytearray
                The frame in its raw bytearray form.
                
            """

            self.frame = self._frame_out
            """Wraps the raw version using the Frame object.
            
            Use frame([index], [new_frame]) to write the frame more easily.
            
            Note
            ----
            if `new_frame` is set, nothing will be returned.
            
            Parameters
            ----------
            index : optional[int]
                Index of the frames, from 0 to 2.
            new_frame : optional[Frame]
                A new frame to copy into the frame buffer.
                
            Returns
            -------
            Frame
                A Frame object with accessible pixels.
                
            """

            self.frame_index = self._display.frame_index
            """Get the frame index.
            
            Use frame_index([new_frame_index]) to access the frame index.
            If `new_frame_index` is not specified, get the current frame index.
            If `new_frame_index` is specified, set the current frame to the 
            new index. 

            Parameters
            ----------
            new_frame_index : optional[int]
                Index of the frames, from 0 to 2.
                
            Returns
            -------
            int
                The index of the active frame.
                
            """

            self.frame_index_next = self._display.frame_index_next
            """Change the frame index to the next one.

            Parameters
            ----------
            None
            
            Returns
            -------
            int
                The index of the active frame.
            
            """

            self.frame_width = self._display.frame_width
            """Get the current frame width.

            Parameters
            ----------
            None
            
            Returns
            -------
            int
                The width of the frame.
                
            """

            self.frame_height = self._display.frame_height
            """Get the current frame height.
            
            Parameters
            ----------
            None
            
            Returns
            -------
            int
                The height of the frame.
                
            """

            self.frame_addr = self._display.frame_addr
            """Get the current frame address.
            
            Parameters
            ----------
            i : optional[int]
                Index of the current frame buffer.
            
            Returns
            -------
            int
                Address of the frame, thus current frame buffer.
                
            """

            self.frame_phyaddr = self._display.frame_phyaddr
            """Get the current physical frame address.
            
            Parameters
            ----------
            i : optional[int]
                Index of the current frame buffer.
            
            Returns
            -------
            int
                Physical address of the frame, thus current frame buffer.
                
            """

        else:
            self.direction = 'in'
            if frame_buffer == None:
                self._capture = _video._capture(VDMA_DICT,
                                                GPIO_DICT,
                                                VTC_CAPTURE_ADDR)
            else:
                self._capture = _video._capture(VDMA_DICT,
                                                GPIO_DICT,
                                                VTC_CAPTURE_ADDR,
                                                frame_buffer)
                                                
            self.frame_buffer = self._capture.framebuffer
                  
            self.stop = self._capture.stop
            """Stop the video controller.
            
            Parameters
            ----------
            None
            
            Returns
            -------
            None
            
            """
            
            self.state = self._capture.state
            """Get the state of the device as an integer value.
            
            Parameters
            ----------
            None
            
            Returns
            -------
            int
                The state 0 (DISCONNECTED), or 1 (STREAMING), or 2 (PAUSED).
                
            """
            
            self.frame_raw = self._capture.frame
            """Get the frame as a bytearray.
            
            User may use frame([index]) to access the frame, which may 
            introduce some overhead in rare cases. The method frame_raw([i]) 
            is faster, but the parameter `i` has to be calculated manually.
            
            Parameters
            ----------
            i : optional[int]
                A location in the bytearray.
                
            Returns
            -------
            bytearray
                The frame in its raw bytearray form.
                
            """
            
            self.frame = self._frame_in
            """Wraps the raw version using the Frame object.
            
            Use frame([index]) to read the frame more easily.
            
            Parameters
            ----------
            index : optional[int]
                Index of the frames, from 0 to 2.
                
            Returns
            -------
            Frame
                A Frame object with accessible pixels.
                
            """

            self.frame_index = self._capture.frame_index
            """Get the frame index.
            
            Use frame_index([new_frame_index]) to access the frame index.
            If `new_frame_index` is not specified, get the current frame index.
            If `new_frame_index` is specified, set the current frame to the 
            new index.

            Parameters
            ----------
            new_frame_index : optional[int]
                Index of the frames, from 0 to 2.

            Returns
            -------
            int
                The index of the active frame.
                
            """

            self.frame_index_next = self._capture.frame_index_next
            """Change the frame index to the next one.

            Parameters
            ----------
            None
            
            Returns
            -------
            int
                The index of the active frame.
            
            """

            self.frame_width = self._capture.frame_width
            """Get the current frame width.

            Parameters
            ----------
            None
            
            Returns
            -------
            int
                The width of the frame.
                
            """

            self.frame_height = self._capture.frame_height
            """Get the current frame height.
            
            Parameters
            ----------
            None
            
            Returns
            -------
            int
                The height of the frame.
                
            """

            self.frame_addr = self._capture.frame_addr
            """Get the current frame address.
            
            Parameters
            ----------
            i : optional[int]
                Index of the current frame buffer.
            
            Returns
            -------
            int
                Address of the frame, thus current frame buffer.
                
            """

            self.frame_phyaddr = self._capture.frame_phyaddr
            """Get the current physical frame address.
            
            Parameters
            ----------
            i : optional[int]
                Index of the current frame buffer.
            
            Returns
            -------
            int
                Physical address of the frame, thus current frame buffer.
                
            """


    def start(self,timeout=20):
        """Start the video controller.
            
        Parameters
        ----------
        timeout : optional[int]
        HDMI controller response timeout in seconds.
        
        Returns
        -------
        None
        
        """
        if timeout<=0:
            raise ValueError("timeout must be greater than 0.")
      
        while self.state() != 1:
            try:        
                self._capture.start()
            except Exception as e:
                if timeout > 0:
                    sleep(1)
                    timeout -= 1
                else:
                    raise e  
           
    def _frame_out(self, *args):
        """Returns the specified frame or the active frame.
        
        Note
        ----
        With no parameter specified, this method returns a new Frame object.
        With 1 parameter specified, this method uses it as the index or frame
        to create the Frame object. 
        With 2 parameters specified, this method treats the first argument as 
        index, while treating the second argument as a frame.
        
        Parameters
        ----------
        *args
            Variable length argument list.
            
        Returns
        -------
        Frame
            An object of a frame in the frame buffer.
            
        """
        if len(args) == 2:
            self._display.frame(args[0], args[1].frame)
        elif len(args) == 1:
            if type(args[0]) is int:
                return Frame(self.frame_width(), self.frame_height(),
                                self._display.frame(args[0]))
            else:
                self._display.frame(args[0].frame)
        else:
            return Frame(self.frame_width(), self.frame_height(),
                         self._display.frame())
    
    def _frame_in(self, index=None):
        """Returns the specified frame or the active frame.
        
        Parameters
        ----------
        index : optional[int]
            The index of a frame in the frame buffer, from 0 to 2.
            
        Returns
        -------
        Frame
            An object of a frame in the frame buffer.
            
        """
        buf = None
        if index is None:
            buf = self._capture.frame()
        else:
            buf = self._capture.frame(index)
        return Frame(self.frame_width(), self.frame_height(), buf)

    def __del__(self):
        """Delete the HDMI object.
        
        Stop the video controller first to avoid odd behaviors of the DMA.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        
        """
        self.stop()  
        if hasattr(self, '_capture'):
            del self._capture
        elif hasattr(self, '_display'):
            del self._display
            
class VGA(object):
    """Class for a VGA controller.

    The frame buffer in a VGA object can be shared among different objects.
    e.g., a VGA object and an HDMI object can use the same frame buffer.
    
    Note
    ----
    Currently VGA only supports direction 'out'.
    
    Examples
    --------
    >>> vga = VGA('out', frame_buffer)
    
    Attributes
    ----------
    direction : str
        Can only be 'out' for VGA to be output.
    frame_buffer : _framebuffer
        A frame buffer storing at most 3 frames.
        
    Raises
    ------
    ValueError
        If direction is not set to 'out'.
        
    """

    def __init__(self, direction, frame_buffer=None):
        """Returns a new instance of a VGA object. 
        
        Assign the given frame buffer if specified, otherwise create a new 
        frame buffer.
        
        Note
        ----
        Currently VGA only supports direction 'out'.
        
        Parameters
        ----------
        direction : str
            Can only be 'out' for VGA to be output.
        frame_buffer : optional[_framebuffer] 
            A frame buffer storing at most 3 frames.
        
        """
        if not direction.lower() == 'out':
            raise ValueError("Currently VGA only supports output.")
        else:
            self.direction = 'out'
            if frame_buffer == None:
                self._display = _video._display(VDMA_DICT,
                                                VTC_DISPLAY_ADDR,
                                                DYN_CLK_ADDR, 1)
            else:
                self._display = _video._display(VDMA_DICT,
                                                VTC_DISPLAY_ADDR,
                                                DYN_CLK_ADDR, 1,
                                                frame_buffer)
                                                
            self.frame_buffer = self._display.framebuffer
            
            self.start = self._display.start
            """Start the video controller.
            
            Parameters
            ----------
            None
            
            Returns
            -------
            None
            
            """

            self.stop = self._display.stop
            """Stop the video controller.
            
            Parameters
            ----------
            None
            
            Returns
            -------
            None
            
            """

            self.state = self._display.state
            """Get the state of the device as an integer value.
            
            Parameters
            ----------
            None
            
            Returns
            -------
            int
                The state 0 (STOPPED), or 1 (RUNNING).
                
            """

            self.mode = self._display.mode
            """Change the resolution of the display. 
            
            Users can use mode(new_mode) to change the resolution.
            Specifically, with `new_mode` to be:
            0 : '640x480@60Hz'
            1 : '800x600@60Hz'
            2 : '1280x720@60Hz'
            3 : '1280x1024@60Hz'
            4 : '1920x1080@60Hz'           
            
            If `new_mode` is not specified, return the current mode.

            Parameters
            ----------
            new_mode : int
                A mode index from 0 to 4.
                
            Returns
            -------
            str
                The resolution of the VGA display.
                
            Raises
            ------
            ValueError
                If `new_mode` is out of range.
                
            """

            self.frame_raw = self._display.frame
            """Returns a bytearray of the frame.
            
            User may use frame([index]) to access the frame, which may 
            introduce some overhead in rare cases. The method 
            frame_raw([i],[new_frame]) is faster, but the parameter `i` has 
            to be calculated manually.

            Note
            ----
            If `new_frame` is set, this method will take the bytearray 
            (`new_frame`) and overwrites the current frame (or the frame 
            specified by `i`). Also, if `new_frame` is set, nothing will 
            be returned.
            
            Parameters
            ----------
            i : optional[int]
                A location in the bytearray.
            new_frame: optional[bytearray]
                A bytearray that can be used to overwrite the frame.
                
            Returns
            -------
            bytearray
                The frame in its raw bytearray form.
                
            """

            self.frame = self._frame_out
            """Wraps the raw version using the Frame object.
            
            Use frame([index], [new_frame]) to write the frame more easily.
            
            Note
            ----
            if `new_frame` is set, nothing will be returned.
            
            Parameters
            ----------
            index : optional[int]
                Index of the frames, from 0 to 2.
            new_frame : optional[Frame]
                A new frame to copy into the frame buffer.
                
            Returns
            -------
            Frame
                A Frame object with accessible pixels.
                
            """

            self.frame_index = self._display.frame_index
            """Get the frame index.
            
            Use frame_index([new_frame_index]) to access the frame index.
            If `new_frame_index` is not specified, get the current frame index.
            If `new_frame_index` is specified, set the current frame to the 
            new index. 

            Parameters
            ----------
            new_frame_index : optional[int]
                Index of the frames, from 0 to 2.
                
            Returns
            -------
            int
                The index of the active frame.
                
            """

            self.frame_index_next = self._display.frame_index_next
            """Change the frame index to the next one.

            Parameters
            ----------
            None
            
            Returns
            -------
            int
                The index of the active frame.
            
            """

            self.frame_width = self._display.frame_width
            """Get the current frame width.

            Parameters
            ----------
            None
            
            Returns
            -------
            int
                The width of the frame.
                
            """

            self.frame_height = self._display.frame_height
            """Get the current frame height.
            
            Parameters
            ----------
            None
            
            Returns
            -------
            int
                The height of the frame.
                
            """

    def _frame_out(self, *args):
        """Returns the specified frame or the active frame.
        
        Note
        ----
        With no parameter specified, this method returns a new Frame object.
        With 1 parameter specified, this method uses it as the index or frame
        to create the Frame object. 
        With 2 parameters specified, this method treats the first argument as 
        index, while treating the second argument as a frame.
        
        Parameters
        ----------
        *args
            Variable length argument list.
            
        Returns
        -------
        Frame
            An object of a frame in the frame buffer.
            
        """
        if len(args) == 2:
            self._display.frame(args[0], args[1].frame)
        elif len(args) == 1:
            if type(args[0]) is int:
                return Frame(self.frame_width(), self.frame_height(),
                                self._display.frame(args[0]))
            else:
                self._display.frame(args[0].frame)
        else:
            return Frame(self.frame_width(), self.frame_height(),
                         self._display.frame())

    def __del__(self):
        """Delete the HDMI object.
        
        Stop the video controller first to avoid odd behaviors of the DMA.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        
        """
        self.stop()
        if hasattr(self, '_capture'):
            del self._capture
        elif hasattr(self, '_display'):
            del self._display
            
class Frame(object):
    """This class exposes the bytearray of the video frame buffer.

    Note
    ----
    The maximum frame width is 1920, while the maximum frame height is 1080.
    
    Attributes
    ----------
    frame : bytearray
        The bytearray of the video frame buffer.
    width : int
        The width of a frame.
    height : int
        The height of a frame.
        
    """

    def __init__(self, width, height, frame=None):
        """Returns a new Frame object.
        
        Note
        ----
        The maximum frame width is 1920; the maximum frame height is 1080.
        
        Parameters
        ----------
        width : int
            The width of a frame.
        height : int
            The height of a frame.
            
        """
        if frame is not None:
            self._framebuffer = None
            self.frame = frame
        else:
            # Create a framebuffer with just 1 frame
            self._framebuffer = _video._frame(1)
            # Create an empty frame
            self.frame = self._framebuffer(0)
        self.width = width
        self.height = height

    def __getitem__(self, pixel):
        """Get one pixel in a frame.

        The pixel is accessed in the following way: 
            `frame[x, y]` to get the tuple (r,g,b) 
        or 
            `frame[x, y][rgb]` to access a specific color.
            
        Examples
        --------
        Get the three component of pixel (48,32) as a tuple, assuming the 
        object is called `frame`:
        
        >>> frame[48,32]
        (128,64,12)

        Access the green component of pixel (48,32):
        >>> frame[48,32][1]
        64
        
        Note
        ----
        The original frame stores pixels as (g,b,r). Hence, to return a tuple 
        (r,g,b), we need to return (self.frame[offset+2], self.frame[offset],
        self.frame[offset+1]).
            
        Parameters
        ----------
        pixel : list
            A pixel (r,g,b) of a frame.
            
        Returns
        -------
        list
            A list of the current values (r,g,b) of the pixel.
            
        """
        x, y = pixel
        if 0 <= x < self.width and 0 <= y < self.height:
            offset = 3 * (y * MAX_FRAME_WIDTH + x)
            
            return self.frame[offset+2],self.frame[offset],\
                    self.frame[offset+1]
        else:
            raise ValueError("Pixel is out of the frame range.")

    def __setitem__(self, pixel, value):
        """Set one pixel in a frame.

        The pixel is accessed in the following way: 
            `frame[x, y] = (r,g,b)` to set the entire tuple
        or 
            `frame[x, y][rgb] = value` to set a specific color.

        Examples
        --------
        Set pixel (0,0), assuming the object is called `frame`:
        
        >>> frame[0,0] = (255,255,255)
        
        Set the blue component of pixel (0,0) to be 128
        
        >>> frame[0,0][2] = 128
        
        Note
        ----
        The original frame stores pixels as (g,b,r).
        
        Parameters
        ----------
        pixel : list
            A pixel (r,g,b) of a frame.
        value : list
            A list of the values (r,g,b) to be set for the pixel.
            
        Returns
        -------
        None
        
        """
        x, y = pixel
        if 0 <= x < self.width and 0 <= y < self.height:
            offset = 3 * (y * MAX_FRAME_WIDTH + x)
            self.frame[offset + 2] = value[0]
            self.frame[offset] = value[1]
            self.frame[offset + 1] = value[2]
        else:
            raise ValueError("Pixel is out of the frame range.")

    def __del__(self):
        """Delete the frame buffer.
        
        Delete the frame buffer and free the memory only if the frame buffer 
        is not empty.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        
        """
        if self._framebuffer is not None:
            del self._framebuffer

    def save_as_jpeg(self, path):
        """Save a video frame to a JPEG image.

        Note
        ----
        The JPEG filename must be included in the path.
        
        Parameters
        ----------
        path : str
            The path where the JPEG will be saved.
            
        Returns
        -------
        None
        
        """
        rgb = bytearray()
        for i in range(self.height):
            row = self.frame[i * MAX_FRAME_WIDTH * 3 :\
                                (i * MAX_FRAME_WIDTH + self.width) * 3]
            rgb.extend(bytearray(
                        chain.from_iterable((row[j+2], row[j], row[j+1])\
                            for j in range(0, len(row)-1, 3))))

        image = Image.frombytes('RGB', (self.width,self.height), bytes(rgb))
        image.save(path, 'JPEG')

    @staticmethod
    def save_raw_as_jpeg(path, frame_raw, width, height):
        """Save a video frame (in bytearray) to a JPEG image.
        
        Note
        ----
        This is a static method of the class.

        Parameters
        ----------
        path : str
            The path where the JPEG will be saved.
        frame_raw : bytearray
            The video frame to be saved.
        width : int
            The width of the frame.
        height : int
            The height of the frame.
            
        Returns
        -------
        None
        
        """
        rgb = bytearray()
        for i in range(height):
            row = frame_raw[i * MAX_FRAME_WIDTH * 3 :\
                            (i * MAX_FRAME_WIDTH + width) * 3]
            rgb.extend(bytearray(
                        chain.from_iterable((row[j+2], row[j], row[j+1])\
                           for j in range(0, len(row)-1, 3))))

        image = Image.frombytes('RGB', (width, height), bytes(rgb))
        image.save(path, 'JPEG')
        