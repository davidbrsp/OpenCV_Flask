from flask import Flask, Response, render_template, request, redirect, url_for
from time import localtime, strftime
import cv2
import numpy as np
import os, glob

principalpath = [ ]
img1show = False
img1path = [ ]
img2show = False
img2path = [ ]
croppedshow = False
croppedpath = [ ]
binarizedshow = False
binarizedpath = [ ]
subtractedshow = False
subtractedpath = [ ]
facesshow = False
facespath = [ ]
video = [ ]
camerashow = False

#workflow = { "workflow" : [ { } ] }
workflow = { "workflow" : [ ] }

app = Flask( __name__ )

@app.context_processor
def inject_workflow( ) :
  global workflow
  return workflow

@app.route( '/startcamera' )
def startcamera( ) :
  global video
  global camerashow

  if not camerashow:
    video = cv2.VideoCapture( 0 )
    camerashow = True
  return renderindex( )

#video = startcamera( )

@app.route( '/' )
@app.route( '/index' )
def index( ) :
  return render_template("/index.html")

def stream( video ):
  """ stream(img) -> None: Esse bloco simplesmente mostra a imagem de entrada na pagina (praticamente um streaming da camera). """
  while True:
    _, image = video.read()
    _, jpeg = cv2.imencode('.jpg', image)
    frame = jpeg.tobytes()
    #frame = image.tobytes()
    yield (b'--frame\r\n'
           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route( '/video_feed' )
def video_feed( ):
    global video
    return Response(stream(video), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route( '/stopcamera' )
def stopcamera( ):
  global video
  global camerashow
  video.release()
  camerashow = False
  return renderindex( )

def renderindex( ) :
  global principalpath
  global img1show
  global img1path
  global img2show
  global img2path
  global croppedshow
  global croppedpath
  global binarizedshow
  global binarizedpath
  global subtractedshow
  global subtractedpath
  global facesshow
  global facespath
  global camerashow

  return render_template( 'index.html', Camerashow = camerashow, Img1path = img1path, Img2path = img2path, Img1show = img1show, Img2show = img2show, Croppedpath = croppedpath, Croppedshow = croppedshow, Binarizedpath = binarizedpath, Binarizedshow = binarizedshow, Subtractedpath = subtractedpath, Subtractedshow = subtractedshow, Facespath = facespath, Facesshow = facesshow )


def run_workflow( ) :
  global workflow
  lwf = len( workflow[ "workflow" ] )
  for i in range( lwf ) :
    if workflow[ "workflow" ][ i ]['operation'] == 'crop' and lwf > 1 :
      workflow[ "workflow" ][ i ]['inpath'] = workflow[ "workflow" ][ i - 1 ]['outpath']
      workflow[ "workflow" ][ i ] = crop2( workflow[ "workflow" ][ i ] )

    # elif i['operation'] == 'binarize':
    #   pass
    # elif i['operation'] == 'delete' :
    #   pass
  return renderindex( )


@app.route('/addjob',  methods = [ 'POST', 'GET' ] )
def addjob( ):
  ''' workflow = { "workflow" : [ { 'name' : 'joao' }, { 'name' : 'jose' },{ 'nome' : 'maria' } ] } '''
  # a.insert(index,obj)
  # a.append(obj)
  global workflow
  # idx = int( request.args.get( 'idx' ) )
  # obj = int( request.args.get( 'obj' ) )
  dictargs = request.args.to_dict( )
  dictreturn = {
    'operation'  : dictargs.pop('operation'),
    'inpath'     : '',
    'outpath'    : '',
    'parameters' : dictargs
  }

#  workflow[ 'workflow' ].insert( idx, obj )
  workflow[ 'workflow' ].append( dictreturn )
  return run_workflow( )
#  return renderindex( )

@app.route('/deljob',  methods = [ 'POST', 'GET' ] )
def deljob( ):
  # a.remove( obj )
  # a.pop( index ) -> a[ index ]
  # a.pop( ) -> a[ -1 ]
  global workflow
  idx = int( request.args.get( 'idx' ) )
#  workflow[ 'workflow' ].remove(obj)
  workflow[ 'workflow' ].pop( idx )
  return renderindex()



@app.route('/camera')
def camera( ):
  """ camera() -> img: Esse bloco não possui entradas, sua saída é uma imagem capturada pela câmera. """
  global video
  CAPTURES_DIR = "static/captures/"
  global workflow

  _, frame = video.read( )
  timestamp = strftime( "%d-%m-%Y-%Hh%Mm%Ss", localtime( ) )
  filename = CAPTURES_DIR + timestamp + ".jpg"
 #  print(f'filename_camera(): { filename }')
  if not cv2.imwrite( filename, frame ) :
    raise RuntimeError( "Unable to capture image " + timestamp )
  print( f'camera().timestamp: { timestamp }' )
  
  dictreturn = {
    "operation"  : "camera",
    "inpath"     : "",
    "outpath"    : timestamp + ".jpg",
    "parameters" : {}
  }

  workflow[ 'workflow' ].append( dictreturn )
  return redirect( url_for( 'show_capture', timestamp = timestamp ) )


@app.route( '/capture/image/<timestamp>', methods = [ 'POST', 'GET' ] )
def show_capture( timestamp ):
  global img1path
  global img2path
  global img1show
  global img2show
  global principalpath

  if img1path != [ ] :
    img2path = img1path
    img2show = True
#  img1path = 'captures/' + timestamp + ".jpg"
  img1path = timestamp + ".jpg"
  principalpath = img1path
  img1show = True
  return renderindex( )


#@app.route( '/crop/captures/<imgPath>/<x>/<y>/<dx>/<dy>',methods=[ 'POST', 'GET' ] )
@app.route( '/crop', methods = [ 'POST', 'GET' ] )
def crop( ) :
  #def crop( img, x, y, dx, dy ) :
  """ crop (img, x, y, dx, dy) -> img: Cropa / fatia o ndarray de entrada em um retângulo. Retorna um ndarray img. """
  global croppedpath
  global croppedshow
  global principalpath
 #  croppedpath = request.args.get( 'imgPath' )
  x  = int( request.args.get( 'x'  ) )
  y  = int( request.args.get( 'y'  ) )
  dx = int( request.args.get( 'dx' ) )
  dy = int( request.args.get( 'dy' ) )

  img = cv2.imread( 'static/captures/' + principalpath )
  if x < 0 or dx < 0 or x > img.shape[ 0 ] or dx > img.shape[ 0 ]  or y < 0 or dy < 0 or y > img.shape[ 1 ] or dy > img.shape[ 1 ] : 
    croppedimg  = img[ x:dx, y:dy ] # crop
    croppedpath = principalpath[ :-4 ] + '_cropped.jpg'
    if not cv2.imwrite( 'static/captures/' + croppedpath, croppedimg ) :
      croppedshow = False
      raise RuntimeError( "Unable to write image " + croppedpath )
    croppedshow = True
    principalpath = croppedpath
  else :
    croppedshow = False
    print(f'Out of Bounds!')
  
  dictreturn = {
    "operation"  : "crop",
    "inpath"     : principalpath,
    "outpath"    : croppedpath,
    "parameters" : [ x, y, dx, dy ]
  }
#  workflow[ 'workflow' ].insert( -1, dictreturn )
  workflow[ 'workflow' ].append( dictreturn )
  #addjob( -1, dictreturn )
  #  return path

def crop2( jobdict ) :
  #def crop( img, x, y, dx, dy ) :
  """ crop (img, x, y, dx, dy) -> img: Cropa / fatia o ndarray de entrada em um retângulo. Retorna um ndarray img. """
  global croppedpath
  global croppedshow
  global principalpath
 #  croppedpath = request.args.get( 'imgPath' )
  # x  = int( request.args.get( 'x'  ) )
  # y  = int( request.args.get( 'y'  ) )
  # dx = int( request.args.get( 'dx' ) )
  # dy = int( request.args.get( 'dy' ) )
  param = jobdict[ 'parameters' ]
  x  = int( param[ 'x'  ] )
  y  = int( param[ 'y'  ] )
  dx = int( param[ 'dx' ] )
  dy = int( param[ 'dy' ] )

  img = cv2.imread( 'static/captures/' + jobdict[ 'inpath' ] )
  if not ( x < 0 or dx < 0 or x > img.shape[ 0 ] or dx > img.shape[ 0 ] or y < 0 or dy < 0 or y > img.shape[ 1 ] or dy > img.shape[ 1 ] ) : 
    croppedimg  = img[ x:dx, y:dy ] # crop
    croppedpath = jobdict[ 'inpath' ][ :-4 ] + '_cropped.jpg'
    if not cv2.imwrite( 'static/captures/' + croppedpath, croppedimg ) :
      croppedshow = False
      jobdict['error'] = f'Unable to write image: { croppedpath }'
      raise RuntimeError( jobdict[ 'error' ] )
    croppedshow = True
    principalpath = croppedpath
    jobdict[ 'outpath' ] = croppedpath
  else :
    croppedshow = False
    jobdict[ 'error' ] = f'Out of Bounds!'
    print( jobdict[ 'error' ] )
  
  # dictreturn = {
  #   "operation"  : jobdict['operation'],
  #   "inpath"     : jobdict['inpath'],
  #   "outpath"    : jobdict['outpath'],
  #   "parameters" : 
  # }
#  workflow[ 'workflow' ].insert( -1, dictreturn )
#  workflow[ 'workflow' ].append( dictreturn )
  #addjob( -1, dictreturn )
  #  return path
  return jobdict
#  return renderindex( )

@app.route( '/binarize', methods = [ 'POST', 'GET' ] )
def binarize( ) :
  """ binarize(img, r, g, b, k) -> img: Retorna uma máscara binarizada da seguinte forma: Out[i, j] = ( Input[i, j, 0]*r + Input[i, j, 1]*g + Input[i, j, 2]*b ) > k
  # formato opencv BGR
  #imgbin[ : , : , 0 ] = img[ : , : , 2 ] * R + img[ : , : , 1 ] * G + img[ : , : , 0 ] * B > k
  # formato RGB
  #  imgbin[ : ] = img[ : , : , 0 ] * R + img[ : , : , 1 ] * G + img[ : , : , 2 ] * B """

  global binarizedshow
  global binarizedpath
  B = int( request.args.get( 'B' ) )
  G = int( request.args.get( 'G' ) )
  R = int( request.args.get( 'R' ) )
  k = int( request.args.get( 'k' ) )

  img = cv2.imread( 'static/captures/' + principalpath )
  imgbin = np.zeros( ( img.shape[ 0 ], img.shape[ 1 ], 1 ), np.int32 )

  for i in range( img.shape[ 0 ] ) :
    for j in range( img.shape[ 1 ] ) :
      value = img.item( i , j , 2 ) * R + img.item( i , j , 1 ) * G + img.item( i , j , 0 ) * B
      if value > k :
        imgbin[ i , j , 0 ] = 255
      else :
        imgbin[ i , j , 0 ] = 0
  binarizedpath = principalpath[ :-4 ] + '_binarized.jpg'  
  if not cv2.imwrite( 'static/captures/' + binarizedpath, imgbin ) :
    raise RuntimeError( "Unable to capture image " + binarizedpath )
  binarizedshow = True

  dictreturn = {
    "operation"  : "binarize",
    "inpath"     : principalpath,
    "outpath"    : binarizedpath,
    "parameters" : [ ]
  }
#  workflow[ 'workflow' ].insert( -1, dictreturn )
  workflow[ 'workflow' ].append( dictreturn )

#  addjob( -1, dictreturn )

  return renderindex( )

@app.route( '/background_subtract', methods = [ 'POST', 'GET' ] )
def background_subtract( ) :
  """ background_subtract(oimg, img) -> img: Subtrai a imagem atual de uma outra anterior. Retorna um ndarray. """
  
  global principalpath
  global img1path
  global img2path
  global subtractedshow
  global subtractedpath

  img1 = cv2.imread( 'static/captures/' + img1path )
  img2 = cv2.imread( 'static/captures/' + img2path )
  sub = cv2.subtract(img1, img2)
#  sub = cv2.subtract(img2, img1)
  subtractedpath = principalpath[ :-4 ] + '_subtracted.jpg'  
  if not cv2.imwrite( 'static/captures/' + subtractedpath, sub ) :
    raise RuntimeError( "Unable to capture image " + subtractedpath )
  subtractedshow = True

  dictreturn = {
    "operation"  : "background_subtract",
    "inpath"     : principalpath,
    "outpath"    : subtractedpath,
    "parameters" : [ ]
  }
#  workflow[ 'workflow' ].insert( -1, dictreturn )
  workflow[ 'workflow' ].append( dictreturn )

#  addjob( -1, dictreturn )



  return renderindex( )

#def lambda(*args, **kwargs):
  """ lambda(*args, **kwargs) -> ret: O bloco lambda permite a definição de um  trecho de código qualquer escrito pelo usuário dinamicamente. """

@app.route( '/detect_faces', methods = [ 'POST', 'GET' ] )
def detect_faces( ):
  """ detect_faces() -> (img, x, y, dx, dy): Detecta um rosto na imagem. Além de retornar um ndarray com um retângulo desenhado no contorno do rosto, o bloco retorna as posições do rosto (X, Y, dX, dY). Que tal implementar como um bloco Lambda? """

  global principalpath
  global facesshow
  global facespath
  
  face_cascade = cv2.CascadeClassifier( 'static/' + 'haarcascade_frontalface_default.xml' )
  img   = cv2.imread( 'static/captures/' + principalpath )
  gray  = cv2.cvtColor( img, cv2.COLOR_BGR2GRAY )
  faces = face_cascade.detectMultiScale( gray, 1.3, 5 )
  for ( x, y, w, h ) in faces:
    img = cv2.rectangle( img, ( x, y ), ( x + w, y + h ), ( 255, 0, 0 ), 2 )
  facespath = principalpath[ :-4 ] + '_faces.jpg'  
  if not cv2.imwrite( 'static/captures/' + facespath, img ) :
    raise RuntimeError( "Unable to capture image " + facespath )
  facesshow = True

  dictreturn = {
    "operation"  : "detect_faces",
    "inpath"     : principalpath,
    "outpath"    : facespath ,
    "parameters" : [ ]
  }
#  workflow[ 'workflow' ].insert( -1, dictreturn )
  workflow[ 'workflow' ].append( dictreturn )

  #addjob( -1, dictreturn )
  return renderindex( )

def clean_cache :
  for i in glob.glob( 'static/captures/*.jpg' ) :
    try:
      os.chmod( i, 0o777 )
      os.remove( i )
    except OSError:
      print(f'Problem on remove { i }')



if __name__ == '__main__':



  # try : 
  #   os.remove( 'static/captures/*.jpg' )
  # except : pass
  app.run( host = '0.0.0.0', threaded = True, debug = True )