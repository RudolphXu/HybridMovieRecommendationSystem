from Model import Model
class SVDModel(Model):

### Construct ###    

    def __init__(self,configModel,utils,config,strTrial):
        Model.__init__(self,configModel,utils,strTrial)
        self.configPath = utils.MODEL_CONFIG_PATH   + self.tag + \
                                              '_t' + strTrial
        self.numIter              = config.SVD_NUM_ITER
        self.SVDBufferPath        = utils.SVDFEATURE_BUFFER_BINARY
        self.learningRate         = config.SVD_LEARNING_RATE
        self.regularizationItem   = config.SVD_REGULARIZATION_ITEM
        self.regularizationUser   = config.SVD_REGULARIZATION_USER
        self.regularizationGlobal = config.SVD_REGULARIZATION_GLOBAL
        self.numFactor            = config.SVD_NUM_FACTOR
        self.activeType           = config.SVD_ACTIVE_TYPE
        self.modelOutPath         = utils.SVDFEATURE_MODEL_OUT_PATH
        self.SVDFeatureBinary     = utils.SVDFEATURE_BINARY
        self.SVDFeatureInferBinary= utils.SVDFEATURE_INFER_BINARY

### Setup Data ###

    def setup(self):
        import utils
        import config
        ### Boot to tmp ###
        print("Re-Indexing")
        values = self.reIndex()
        ### Take tmp to feat ###
        print("Setting Up Features")
        self.setupFeatures()
        ### Take feat to run ###
        print("Converting Data")
        self.dataConvert()
        ### Write config file ###
        print("Writing Config")
        self.writeConfig()

    def reIndex(self):
        bootTrainFile = open(self.bootTrain, 'r')
        bootCVFile    = open(self.bootCV   , 'r')
        bootTestFile  = open(self.bootTest , 'r')
        tmpTrainFile  = open(self.tmpTrain,  'w')
        tmpTestFile   = open(self.tmpTest,   'w')
        tmpCVFile     = open(self.tmpCV,     'w')

        ############## Write tmp file reindexed ###############3
        trainLines = bootTrainFile.readlines()
        CVLines    = bootCVFile.readlines()
        testLines  = bootTestFile.readlines()

        fullInput = []
        fullInput.append(trainLines)
        fullInput.append(CVLines)
        fullInput.append(testLines)

        uidDic={}
        iidDic={}
        newuid=1
        newiid=1
        ctr=0  # is the counter of the total number.
        sum=0.0

        #Build dictionary
    
        for line in trainLines:
            arr = line.rsplit('\t')
            uid = int(arr[0].strip())
            iid = int(arr[1].strip())
            rating = int(float(arr[2].strip()))
            #this part for calculating the average
            sum+=rating
            ctr+=1

		    #this part for reindexing the user ID
            if uid not in uidDic:
                uidDic[uid]=newuid
                newuid+=1
		    #this part for reindexing the item ID
            if iid not in iidDic:
                iidDic[iid]=newiid
                newiid+=1
    
        for line in CVLines:
            arr = line.rsplit('\t')
            uid = int(arr[0].strip())
            iid = int(arr[1].strip())
            #this part for reindexing the user ID
            if uid not in uidDic:
                uidDic[uid]=newuid
                newuid+=1
		    #this part for reindexing the item ID
            if iid not in iidDic:
                iidDic[iid]=newiid
                newiid+=1
    
        for line in testLines:
            arr = line.rsplit('\t')
            uid = int(arr[0].strip())
            iid = int(arr[1].strip())
	        #this part for reindexing the user ID
            if uid not in uidDic:
                uidDic[uid]=newuid
                newuid+=1
		    #this part for reindexing the item ID
            if iid not in iidDic:
                iidDic[iid]=newiid
                newiid+=1

        #Re-index
        for line in trainLines:
            arr = line.split()
            uid = int(arr[0].strip())
            iid = int(arr[1].strip())
            rating = int(float(arr[2].strip()))
            tmpTrainFile.write('%d\t%d\t%d\n' %(uidDic[uid],iidDic[iid],rating))
        for line in CVLines:
            arr = line.split()
            uid = int(arr[0].strip())
            iid = int(arr[1].strip())
            rating = int(float(arr[2].strip()))
            tmpCVFile.write('%d\t%d\t%d\n' %(uidDic[uid],iidDic[iid],rating))
        for line in testLines:
            arr = line.split()
            uid = int(arr[0].strip())
            iid = int(arr[1].strip())
            rating = int(float(arr[2].strip()))
            tmpTestFile.write('%d\t%d\t%d\n' %(uidDic[uid],iidDic[iid],rating))

        #calculate different parameter.
    
        self.numUser=len(uidDic)
        self.numMovie=len(iidDic)
        self.avg=sum/ctr
        self.numGlobal = 0
    
        #Close files
        bootTrainFile.close()
        bootTestFile.close()
        bootCVFile.close()
        tmpTrainFile.close()
        tmpTestFile.close()
        tmpCVFile.close()

    def dataConvert(self):
        import os
        os.system(self.SVDBufferPath + ' ' + 
                self.featTrain + ' ' + self.runTrain)
        os.system(self.SVDBufferPath + ' ' + 
                self.featCV    + ' ' + self.runCV   )
        os.system(self.SVDBufferPath + ' ' + 
                self.featTest  + ' ' + self.runTest )

    def writeConfig(self):
        import os
        fout =  open(self.configPath,'w')
        fout.write('#Config file for ' + self.tag + '\n')
        fout.write('#Global Bias\n')
        fout.write('base_score = '    + str(self.avg) + '\n')
        fout.write('#Learning Rate for SGD\n')
        fout.write('learning_rate = ' + self.learningRate + '\n')
        fout.write('#Regularization Constants (\lambda)\n')
        fout.write('wd_item = '       + self.regularizationItem + '\n')
        fout.write('wd_user = '       + self.regularizationUser + '\n')
        fout.write('wd_global = '     + self.regularizationGlobal+'\n')
        fout.write('#Numbers of Features\n')
        fout.write('num_item = '      + str(self.numMovie) + '\n')
        fout.write('num_user = '      + str(self.numUser)  + '\n')
        fout.write('num_global = '    + str(self.numGlobal)+ '\n')
        fout.write('#Number of features\n')
        fout.write('num_factor = '   + self.numFactor + '\n')
        fout.write('#Translation function: 0=linear, 2=sigmoid\n')
        fout.write('active_type = '   + self.activeType + '\n')
        fout.write('#Training dataset\n')
        fout.write('buffer_feature = \"' + self.runTrain + '\"\n')
        fout.write('#Model save path\n')
        fout.write('model_out_folder = \"' + self.modelOutPath
                + self.tag + '_t' + self.trial + '\"')
        os.system('mkdir ' + self.modelOutPath 
                + self.tag + '_t' + self.trial)
        fout.close()

### Setup Features ###

    def setupFeatures(self):
        if self.featureSet == 'Basic':
            self.basicConvert(self.tmpTrain,self.featTrain)
            self.basicConvert(self.tmpCV,   self.featCV)
            self.basicConvert(self.tmpTest, self.featTest)

    def basicConvert(self,fin,fout):
        fi = open( fin , 'r' )
        fo = open( fout, 'w' )
        #extract from input file    
        for line in fi:
            arr  =  line.split()               
            uid  =  int(arr[0].strip())
            iid  =  int(arr[1].strip())
            score=  int(arr[2].strip())
            fo.write( '%d\t0\t1\t1\t' %score )
            # Print data,user and item features all start from 0
            fo.write('%d:1 %d:1\n' %(uid-1,iid-1))
        fi.close()
        fo.close()

### Run ###

    def run(self,sproc,subprocesses):
        p = sproc.Popen(self.SVDFeatureBinary + ' ' + self.configPath +
             ' num_round=' + self.numIter,shell=True) 
        subprocesses.append(p)

    def fixRun(self):
        import os
        self.predCVTmp   = self.predCV   + '_tmp'
        self.predTestTmp = self.predTest + '_tmp'
        os.system(self.SVDFeatureInferBinary + ' ' + self.configPath +
             ' test:buffer_feature=\"' + self.runCV + '\"' +
             ' pred=' + self.numIter + 
             ' name_pred=' + self.predCVTmp)
        os.system(self.SVDFeatureInferBinary + ' ' + self.configPath +
             ' test:buffer_feature=\"' + self.runTest + '\"'
             ' pred='      + self.numIter +
             ' name_pred=' + self.predTestTmp)
        self.prependUserMovieToPredictions(self.bootCV,self.predCVTmp,self.predCV)
        self.prependUserMovieToPredictions(self.bootTest,self.predTestTmp,self.predTest)       
