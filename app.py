import cv2
import re
import sys
# from detect_custom1 import Load_model
import torch 
from paddleocr import PaddleOCR
import datetime
import pyodbc as odbc


print("helo")
model = torch.hub.load(r'yolov5','custom',path=r'model.pt',source='local')
cap1 = cv2.VideoCapture(r"temp.mp4")
model.conf = 0.70
model.iou= 0.45
frame_track = 2
counter=0

while True:
  try:
    conn = odbc.connect('Driver={SQL Server};''Server=localhost\SQLEXPRESS;''Database=license;''Trusted_Connection=yes;')
    print("connection successful")
  except Exception as e:
    print(e)
    print('task is terminated')
    sys.exit()
  else:
    cursor = conn.cursor()
  
  # insert_statement ="INSERT INTO license_master (licensenumber,placename,timeslot,filepath) VALUES (?, ?, ?, ?)"
  insert_statement ='''DECLARE @timedif int 
  set @timedif = DATEDIFF( MINUTE, (SELECT MAX(timeslot) FROM license_master WHERE licensenumber=?), ?);
  If not exists(SELECT * FROM license_master t1 WHERE t1.timeslot = (SELECT MAX(timeslot) 
  FROM license_master t2 WHERE t2.licensenumber=? and t2.datedifference>@timedif+(SELECT datedifference 
  FROM license_master t3 WHERE t3.licensenumber=? and t3.timeslot=(SELECT MAX(timeslot) 
  FROM license_master t4 WHERE t4.licensenumber=?))-29))
  INSERT INTO license_master (licensenumber,placename,timeslot, filepath, datedifference) 
  VALUES (?, ?, ?, ?,ISNULL(DATEDIFF( Minute, (SELECT MAX(timeslot) FROM license_master s2 WHERE s2.licensenumber=?),?),0));'''
  counter=counter+1
  # Capture frame-by-frame
  ret1, frame1 = cap1.read()
  print(ret1)
  if frame_track >10:
      current_time= datetime.datetime.now()
      frame1 = cv2.rotate(frame1, cv2.ROTATE_90_COUNTERCLOCKWISE)
      if counter <50:
        continue
      result = model(frame1,size=640)
      print("*"*80)
      print("counter ---------------------------------" +str(counter))
      # print(result)
      crop= result.crop()
      # print(crop)
      if crop :
        print("hello")
        frame_track += 1
        #cv2_imshow(crop[0]['im'])
        name="images/L_crop"+ str(frame_track)+".jpg"
        cv2.imwrite(name,crop[0]['im'])
        
        # The path of detection and recognition model must contain model and params files
        ocr = PaddleOCR(lang='en',det_model_dir='models/en_PP-OCRv3_det_infer', rec_model_dir='models/en_PP-OCRv3_rec_infer', cls_model_dir='models/ch_ppocr_mobile_v2.0_cls_infer', use_angle_cls=True)
        result = ocr.ocr(crop[0]['im'], cls=True)
        lines=result
        txt_cleaned= []
        
        #clean the txt using conf and special characters
        for i in lines:
          IND_flag = False
          txt_pred,txt_conf = i[1][0],i[1][1]
          for check in ["IN","IND"]:
            if check in txt_pred:
              IND_flag = True
          if IND_flag == False:
            if txt_conf>0.5:
              txt_cleaned.append(txt_pred)
        print(txt_cleaned)
        state_flag=False
        special_characters = ['.','!','#','$','%', '&','@','[',']',' ',']','_',' ']
        for index,txt in enumerate(txt_cleaned):
          for i in special_characters:
              txt_cleaned[index] = txt_cleaned[index].replace(i,'')
          
        print("cleaned input txt : ",txt_cleaned)

        # check if the state exists and also use that as the starting index
        state_index=0
        check_state=False
        state_flag=False
        states = ["AN","AP","AN","AR","AS","BR","CH","DN","DD","DL","GA","GJ","HR","HP","JK","KA","KL","LD","MP","MH","MN","ML","MZ","NL","OR","PY","PN","RJ","SK","TN","TR","UP","WR"]
        for index,i in enumerate(txt_cleaned):
          print(i[:2])
          check_state= any(ele in i[:2] for ele in states)
          print("state check : "+str(check_state)+"   " + i)
          if check_state:
            state_index=index
            state_flag=True
        print("State present : ",state_flag)

        #concate all the text
        if not state_flag:
          continue
        license_number=""
        for i in txt_cleaned[state_index:]:
          license_number = license_number + i
        print("license list is merged : ", license_number)

        #if the license number is incomplete
        if len(license_number)<7:
          continue
        print("length of license number is more than 7 ")

        print("after cleaning special characters",license_number)
        pattern = "\A[a-zA-Z]{2}\d{2}[a-zA-Z]{2}\d{1,4}\Z"
        if len(license_number)>7:
          m=re.match(pattern,license_number)
          if m :
            print("Final license number : ",license_number)
            print([license_number,str(current_time),"Bengaluru",name])
            records = [license_number,current_time,license_number,license_number,license_number,license_number,"Bengaluru",current_time,name,license_number,current_time]
            try:
              cursor.execute(insert_statement, records)
              cursor = conn.cursor()      
            except Exception as e:
                cursor.rollback()
                print(e)
                print('transaction rolled back')
            else:
                print('records inserted successfully')
                cursor.commit()
                cursor.close()
                conn.close()
            records = []
  else:
      frame_track += 1 
        
# releasecapture
cap1.release()