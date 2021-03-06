import  os
import SimpleITK as sitk
import cv2

def dicom_metainfo(dicm_path, list_tag):
    '''
    获取dicom的元数据信息
    :param dicm_path: dicom文件地址
    :param list_tag: 标记名称列表,比如['0008|0018',]
    :return:
    '''
    reader = sitk.ImageFileReader()
    reader.LoadPrivateTagsOn()
    reader.SetFileName(dicm_path)
    reader.ReadImageInformation()
    res = []
    for tag in list_tag:
        try:
            tmp = reader.GetMetaData(tag)
            res.append(tmp)
        except:
            res.append("nothing!")
            continue
    return res
    # return [reader.GetMetaData(t) for t in list_tag]


def dicom2array(dcm_path):
    '''
    读取dicom文件并把其转化为灰度图(np.array)
    https://simpleitk.readthedocs.io/en/master/link_DicomConvert_docs.html
    :param dcm_path: dicom文件
    :return:
    '''
    image_file_reader = sitk.ImageFileReader()
    image_file_reader.SetImageIO('GDCMImageIO')
    image_file_reader.SetFileName(dcm_path)
    image_file_reader.ReadImageInformation()
    image = image_file_reader.Execute()
    if image.GetNumberOfComponentsPerPixel() == 1:
        image = sitk.RescaleIntensity(image, 0, 255)
        if image_file_reader.GetMetaData('0028|0004').strip() == 'MONOCHROME1':
            image = sitk.InvertIntensity(image, maximum=255)
        image = sitk.Cast(image, sitk.sitkUInt8)
    img_x = sitk.GetArrayFromImage(image)[0]
    return img_x

import glob
import os
import pandas as pd


    # row = pd.Series(
    #     {'studyUid': studyUid, 'seriesUid': seriesUid, 'instanceUid': instanceUid, 'annotation': annotation})
    # annotation_info = annotation_info.append(row, ignore_index=True)


dcm_root = "/home/wang/PycharmProjects/tianchi/lumbar_testA50"
study_roots = glob.glob(os.path.join(dcm_root,"*"))

describe_8_103e = []
describe = []
# pos_lab = []
# neg_lab = []
from collections import  defaultdict

pos_tags = defaultdict(int)
neg_tags = defaultdict(int)

parse_annotations = pd.DataFrame()
val_pathroots = []
for study_root in study_roots:
    dd = defaultdict(list)
    dcm_paths = glob.glob(os.path.join(study_root + "/*.dcm"))
    for dcm_path in dcm_paths:
        sopuids = []
        # for fn in os.listdir(dcm_root):
        #     dcm_path = os.path.join(dcm_root,fn)
        print(dcm_path)
        try:
            img = dicom2array(dcm_path)
        except:
            continue
        print(img.shape)
        list_tag = ['0020|000d', '0020|000e', '0008|0018', '0020|0011','0020|0037','0020|0032','0008|1030','0008|103e']
        # study uid ,series uid, sop uid(frame id) ,第几个序列
        # list_tag = ['0008|0018', '0020|0011','0008|103e']
        # instance id,
        r=dicom_metainfo(dcm_path,list_tag)
        # describe_8_103e.append(r[2])
        if r[2] not in sopuids:
            sopuids.append(r[2])
        else:
            print(dcm_path)
        print(r)
        s = 0.
        if r[4] != "nothing!":
            r4 = [float(i) for i in r[4].split("\\")]
            v = [0,1,0,0,0,-1]
            print(v)
            for i in range(len(v)):
                s = s + r4[i]*v[i]
            print(r4)
        d = r[7]
        dstr = d.encode('UTF-8', 'ignore').decode('UTF-8')
        tmp = []



        cv2.putText(img,str("seriel_num: " + r[3]),(20,100),fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=1.0,thickness=4,color=255)

        cv2.putText(img,str(": " + r[4]),(10,120),fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=0.4,thickness=1,color=255)

        cv2.putText(img,str(": " + r[5]),(10,140),fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=0.4,thickness=1,color=255)
        if s > 1.8:
            cv2.putText(img,"V",(10,160),fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=0.8,thickness=1,color=255)
            tmp.append(dcm_path)

            tmp.append(dstr)
            tmp.append(r[3])
            r5 = [float(i) for i in r[5].split("\\")]
            tmp.append(r5[0])
            describe.append(tmp)
            dd[r[1]].append(tmp)
        # cv2.putText(img,dstr,(10,180),fontFace=cv2.FONT_HERSHEY_SIMPLEX,fontScale=0.8,thickness=1,color=255)
        # cv2.imshow("img",img)
        # save_path = dcm_path.replace("dcm","jpg")
        # cv2.imwrite(save_path,img)
        # cv2.waitKey(10)
    find_t2 = False
    t2_serials = []
    for key in dd.keys():

        dd[key].sort(key=lambda x:x[-1])
        s_tag = dd[key][0][1].upper()

        # neg_tags = [
        #     "T1",
        #     "STIR"
        #     ""
        #
        # ]

        if "T2" in s_tag and "SCOUNT" not in s_tag and "STIR" not in s_tag and len(dd[key]) > 4:
            t2_serials.append(key)





        # have_pos = False
        # for item in dd[key]:
        #     if item[1] == 1:
        #         have_pos = True
        #

        # if(have_pos): #     pos_tags[dd[key][0][2]] += 1
        # else:
        #     neg_tags[dd[key][0][2]] += 1
        # print(dd[key])
    # if len(t2_serials) < 1:
    if len(t2_serials) < 1:
        for key in dd.keys():
            print(dd[key])
            if "count" not in key.lower() and len(dd[key]) > 4 and "stir" not in key.lower():
                t2_serials.append(key)
    print("Len",len(t2_serials))
    len_dict = defaultdict(list)
    new_t2_serials = t2_serials
    if (len(t2_serials) > 1):
        new_t2_serials = []
        for key in t2_serials:
            len_dict[len(dd[key])].append(key)

        for l in len_dict.keys():
            num = 1000
            new_key = len_dict[l][0]
            for k in len_dict[l]:
                path = dd[k][0][0]
                # print("ddk",os.path.basename(path))
                # print(os.path.basename(path)[5:-4])
                tmp_n = int(os.path.basename(path)[5:-4])
                if(tmp_n) < num:
                    new_key = k
                    num = tmp_n
            new_t2_serials.append(new_key)
    # val_pathroots.append( dd[new_t2_serials[0]][0][0])










    for key in new_t2_serials:
        dd_frame = pd.DataFrame(dd[key],columns=('imgpath','tag','series_id','x_axis'))
        print(dd_frame)
        parse_annotations = parse_annotations.append(dd_frame)
        val_pathroots.append(dd[key][int(len(dd[key])/2)][0])
# for key in dd.keys():
#     dd[key].sort(key=lambda x:x[-1])
#     for item in dd[key]:
#         print(item)
print(parse_annotations.head())
# for row in parse_annotations.iterrows():
#     print(row)
parse_annotations.to_csv("valset_new.csv")



with open("val_paths.txt",'w') as fout:
    for item in val_pathroots:
        fout.write(item + '\n')


# with open("pos_tags.txt",'w') as fout:
#     for key in pos_tags:
#         fout.write(key + "," + str(pos_tags[key]) + "\n")
#
# with open("neg_tags.txt",'w') as fout:
#     for key in neg_tags:
#         fout.write(key + "," + str(neg_tags[key]) + "\n")

# with open("test.txt",'w') as fout:
#     for item in describe:
#         print(item)
#         item = [str(i) for i in item]
#         # fout.write()
#         try:
#             tmp = " ".join(item)
#             fout.write(tmp + "\n")
#         except:
#             continue


# for item in describe_8_103e:
#     print(item)