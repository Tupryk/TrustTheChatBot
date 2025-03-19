# Trust The ChatBot

## Install
Clone the repository and the necessary submodules
```
git clone https://github.com/Tupryk/TrustTheChatBot
cd TrustTheChatBot
git submodule init
git submodule update
```
Install the necessary dependencies
```
pip install -r requirements.txt
```
Add a front facing camera to your pandaSingle.g scene if you use scene images for inference.
```
cameraWrist(l_panda_joint7): {
 Q: [0.0566288, -0.0138618, 0.158583, 0.371288, -0.0124238, 0.0272688, -0.928034]
#, Q: "d(180 0 1 0) d(-45 0 0 1) t(-.03 -.045 -.16) t(0 0 .01)",
 shape: camera, size: [.1],
 focalLength: 0.895, width: 640, height: 360, zRange: [.1, 10]
}
```

## Test Run
If you have a GPU you can test inference directly on an LLM by running
```
python3 main.py
```
Otherwise you can directly run a BBO test script on a pre-existing LLM output
```
python3 tests/bbo_test.py
```
