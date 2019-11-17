

## 1. Install
```
$ virtualenv -p `whereis python2.7` venv
$ source venv/bin/activate 
$ pip install -r requirements.txt
```


## 2. Run

#### Prepare env.sh
```
echo "COG_USER"
export COG_USER="youremail@abc.com"
echo "COG_PASS"
export COG_PASS='yourpassword'
echo "COG_TENANT"
export COG_TENANT="yourCOG_TENANT"
echo "COG_SUBJECT_ID"
export COG_SUBJECT_ID="yourSubject"

```


#### 3. Patch download google image result
```
$ googleimagesdownload -k cars
```


#### Patch download google image result
```
$ python main.py  $COG_SUBJECT_ID ./images -r
```