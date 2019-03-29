# coding: utf-8
from pydub import AudioSegment
from io import BytesIO
from common import logger,config
import sys,urllib,urllib2,json,base64,hashlib,time
from common import config

reload(sys)
if sys.getdefaultencoding() != 'utf-8':
        sys.setdefaultencoding('utf-8')
        reload(sys)

def v2t(voice_data):
    try:
        wav_file_path = config.wxbot_cache_path + "/out.wav"
        audio = AudioSegment.from_mp3(BytesIO(voice_data))
        audio.export(wav_file_path, format="wav")
        with open(wav_file_path,'rb') as f:
            data = f.read()
            if config.voice2txt_engine=="baidu":
                return _covert2text_baidu(data)
            else:
                return _covert2text_xunfei(data)
    except Exception as e :
        logger.exception(e,"转化语音识别失败"+str(e))
        return None

def _covert2text_baidu(audio):
    from aip import AipSpeech

    """ 你的 APPID AK SK """
    APP_ID = config.voice2txt_app_id
    API_KEY = config.voice2txt_api_key
    SECRET_KEY = config.voice2txt_secret_key
    logger.debug("secret=%s,api_key=%s,appid=%s", SECRET_KEY, API_KEY, APP_ID)
    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

    transform = client.asr(audio, 'wav',8000)
    logger.debug("百度转化的结果为：%r",transform)
    return transform['result'][0]

#调用科大讯飞，直接转成语音
def _covert2text_xunfei(voice_data):
    
    base64_audio = base64.b64encode(voice_data)
    body = urllib.urlencode({'audio': base64_audio})

    url = config.voice2txt_url
    api_key = config.voice2txt_api_key
    param = {"engine_type": "sms8k", "aue": "raw"}
    x_appid = config.voice2txt_app_id
    logger.debug("url=%s,api_key=%s,x_appid=%s",url,api_key,x_appid)

    x_param = base64.b64encode(json.dumps(param).replace(' ', ''))
    x_time = int(int(round(time.time() * 1000)) / 1000)
    x_checksum = hashlib.md5(api_key + str(x_time) + x_param).hexdigest()
    x_header = {'X-Appid': x_appid,
                'X-CurTime': x_time,
                'X-Param': x_param,
                'X-CheckSum': x_checksum}
    req = urllib2.Request(url, body, x_header)
    result = urllib2.urlopen(req)
    result = result.read()
    logger.debug("科大讯飞转化的数据：%r",result)
    json_result = json.loads(result)

    return json_result['data']