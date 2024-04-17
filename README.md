#Description
Faster R-CNN adalah salah satu arsitektur populer dalam deteksi objek yang diperkenalkan oleh Ross Girshick pada tahun 2015. Ada beberapa alasan mengapa tim The Woz memilih beberapa arsitektur tersebut untuk digunakan dalam tugas deteksi objek (Project 2):
1. Kecepatan Tinggi
2. Kinerja Tinggi
3. Kemampuan untuk Mendeteksi Objek dalam Berbagai Skala dan Aspek
4. Kemampuan untuk Adaptasi
5. Ketersediaan Implementasi dan Dukungan Komunitas

#Dataset dan Review hasil
Dataset yang digunakan adalah Coco2017 - class “Person”.

<img width="521" alt="image" src="https://github.com/alnybera/Project2-PersonTracking-PersonDetection/assets/163568585/3b319b1b-e4e7-4786-a03c-3311d9417168">

Project kali ini menerapkan object detection improvement dengan Augmentation --> random flip transform dan Pre-trained yang digunakan : torchvision.models.detection.fasterrcnn_resnet50_fpn.
Selain itu project ini menerapkan NMS (Non-Maximum Suppression) dimana NMS merupakan teknik yang umum digunakan dalam deteksi objek untuk mengatasi masalah tumpang tindih atau duplikasi yang dihasilkan oleh proses deteksi objek. Teknik ini bekerja dengan cara memfilter deteksi yang tumpang tindih dan hanya mempertahankan deteksi yang paling relevan.

<img width="392" alt="image" src="https://github.com/alnybera/Project2-PersonTracking-PersonDetection/assets/163568585/d8a452e6-70e9-4ab3-91d6-f30f1b8cd51c">


<img width="451" alt="image" src="https://github.com/alnybera/Project2-PersonTracking-PersonDetection/assets/163568585/8039efa0-8c1b-44b0-b9c4-d77618d93eb1">


Accumulating evaluation results:
<img width="449" alt="image" src="https://github.com/alnybera/Project2-PersonTracking-PersonDetection/assets/163568585/c8ece5b5-b8e3-4b27-b8ba-98c6d5fadeab">


Hasil yang didapatkan:
<img width="290" alt="image" src="https://github.com/alnybera/Project2-PersonTracking-PersonDetection/assets/163568585/38e057d6-01b2-49a0-a33a-c11ac0907b8d">
