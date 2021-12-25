from rest_framework.response import Response
from rest_framework import status
import cloudinary.uploader
from rest_framework import generics
from product.models import *

class DownloadImageView(generics.GenericAPIView):
    def post(self,request):
        for index,img in enumerate(request.data):
            print('index',index)
            object_id = request.data[index].get('_id')
            files = request.data[index].get('image')
            list_image=ImageList.objects.create(pk=object_id)

            for file in files:
                image_name = str(file['id'])
                image_url = file['url']
                path_of_file = cloudinary.uploader.upload(image_url,use_filename=True,folder=f'liquids/dampfdorado/{object_id}/',public_id=str(image_name))
                # print(111,path_of_file)
                # image = 'v'+str(path_of_file['version'])+path_of_file['public_id']
                ProductImage.objects.create(parent=list_image,image=path_of_file['secure_url'])
        return Response(status=status.HTTP_200_OK, data={'success': True})



