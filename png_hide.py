from PIL import Image
from bitarray import bitarray
import struct
import sys


def store_msg( img, msg ):
  '''Returns a new image which contains the ASCII message in its color channel's
  least significant bits. The message is prepended with a 32-bit value for the
  message's string length. If the message does not fit, None is returned
  instead. Bits beyond the message's length remain unaffected.
  '''
  data = bytearray( struct.pack( '>I', len( msg ) ) )
  data.extend( bytes( msg, 'ASCII' ) )

  num_msg_bits = 8 * len( data )
  num_available_bits = img.width * img.height * 8

  if num_available_bits < num_msg_bits:
    return None

  if img.mode != 'RGB' and img.mode != 'RGBA':
    img = img.convert( 'RGBA' )
  else:
    img = img.copy( )

  pxs = img.load( )

  for i in range( 0, num_msg_bits ):
    src_byte_id = i // 8
    src_bit_id  = i % 8

    px_channel = i % 3
    px_x = ( i // 3 ) % img.width
    px_y = ( i // 3 ) // img.width

    # Note that bit 0 is the /most/ significant bit
    msg_bit_val = ( data[ src_byte_id ] >> ( 7 - src_bit_id ) ) & 1

    px = list( pxs[px_x, px_y] )
    px[px_channel] = ( px[px_channel] & 0xFE ) | msg_bit_val
    pxs[px_x, px_y] = tuple( px )
  
  return img


def read_msg( img ):
  '''Reads the ASCII message stored in the image's color channels their least
  significant bits. The byte message's first 4 bytes must contain the length of
  the ASCII string.

  Warning
  -------
  If the stored message is malformed, this method throws an exception. This
  happens when the bytes represented by the bits are not a valid ASCII string.
  '''
  pxs = img.getdata( )
  bits = bitarray( )

  for px in pxs:
    bits.append( px[ 0 ] & 1 )
    bits.append( px[ 1 ] & 1 )
    bits.append( px[ 2 ] & 1 )

  bs = bytes( bits )

  msg_len = struct.unpack( '>I', bs[0:4] )[0]
  return bs[4:4+msg_len].decode( 'ASCII' )


################################################################################
# # # # # # # # # # # # # # # # # # # MAIN # # # # # # # # # # # # # # # # # # #
################################################################################


if __name__ == '__main__':
  img = Image.open( 'example_input.png' )
  img2 = store_msg( img, 'Goats are like mushrooms')

  if img2 == None:
    print( 'The image has insufficient pixels to store the message' )
    sys.exit(0)
    
  img2.save( 'output.png' )

  # Read the message back
  img3 = Image.open( 'output.png' )
  print( read_msg( img3 ) )
