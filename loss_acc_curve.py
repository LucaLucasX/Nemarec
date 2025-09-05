#!/usr/bin/env python
# coding: utf-8

# In[10]:


#insert list of loss values
Alex_loss=[]
VGG16_loss=[]
VGG19_loss=[]
ResNet34_loss=[]
ResNet50_loss=[]
ResNet101_loss=[]
DenseNet121_loss=[]
inception_loss=[]
xeption_loss=[]
x=range(len(train_loss))
print(x)


# In[14]:


#loss curve
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Times New Roman"
plt.figure(figsize=(10,6),dpi=100)
ax = plt.axes()
ax.set_facecolor("white")
plt.plot(x,Alex_loss,'-')
plt.plot(x,VGG16_loss,'-')
plt.plot(x,VGG19_loss,'-')
plt.plot(x,ResNet34_loss,'-')
plt.plot(x,ResNet50_loss,'-')
plt.plot(x,ResNet101_loss,'-')
plt.plot(x,DenseNet121_loss,'-')
plt.plot(x,inception_loss,'-')
plt.plot(x,xeption_loss,'-')
plt.xticks(range(len(x))[::10],fontsize=20)
plt.yticks(range(6),fontsize=20)
plt.xlabel('epoch',fontsize=24,fontstyle='normal')
plt.ylabel('loss',fontsize=24,fontstyle='normal')
plt.legend(['Alex loss','VGG16 loss','VGG19 loss','ResNet34 loss','ResNet50 loss','ResNet 101','Densenet121','inception v3','xeption'],fontsize=20)
plt.grid('True')
#plt.grid('True',color='k', linestyle='-', linewidth=2)
#save_path='./Desktop/'+'plot'+'.png'
#plt.savefig(save_path)


# In[ ]:


#insert the test accuracy
Alex_acc=[]
VGG16_acc=[]
VGG19_acc=[]
ResNet34_acc=[]
ResNet50_acc=[]
ResNet101_acc=[]
DenseNet121_acc=[]
inception_acc=[]
xeption_acc=[]
x=range(len(Alex_acc))
print(x)


# In[ ]:


#test acc curve
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Times New Roman"
plt.figure(figsize=(10,6),dpi=100)
ax = plt.axes()
ax.set_facecolor("white")
plt.plot(x,Alex_acc,'-')
plt.plot(x,VGG16_acc,'-')
plt.plot(x,VGG19_acc,'-')
plt.plot(x,ResNet34_acc,'-')
plt.plot(x,ResNet50_accs,'-')
plt.plot(x,ResNet101_accs,'-')
plt.plot(x,DenseNet121_acc,'-')
plt.plot(x,inception_acc,'-')
plt.plot(x,xeption_acc,'-')
plt.xticks(range(len(x))[::10],fontsize=20)
plt.yticks(range(6),fontsize=20)
plt.xlabel('epoch',fontsize=24,fontstyle='normal')
plt.ylabel('loss',fontsize=24,fontstyle='normal')
plt.legend(['Alex loss','VGG16 loss','VGG19 loss','ResNet34 loss','ResNet50 loss','ResNet 101','Densenet121','inception v3','xeption'],fontsize=20)
plt.grid('True')

