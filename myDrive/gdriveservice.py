from __future__ import print_function
import pickle, io, random, string
import os.path
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class drive:
    def setService(self):
        # change to the subfolder where the credentials (should be) are
        dir = os.getcwd()
        os.chdir(dir + '\myDrive')

        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # get credentials.json
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        # change back directories
        os.chdir(dir)
        
        return build('drive', 'v3', credentials=creds)

    def printLastFiles(self, num=10):
        # Call the Drive v3 API
        results = self.service.files().list(
            pageSize=num, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print(u'{0} ({1})'.format(item['name'], item['id']))

    def getFileIdByName(self, fileName):
        query = "name='" + fileName + "'"
        page_token = None
        while True:
            response = self.service.files().list(q=query,
                                                spaces='drive',
                                                fields='nextPageToken, files(id, name)',
                                                pageToken=page_token).execute()
            for file in response.get('files', []):
                # Process change
                return file.get('id')
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

    def downloadFileById(self, id, path):
        file_id = str(id)
        request = self.service.files().get_media(fileId=file_id)
        fh = io.FileIO(path + self.randomStringName(6) + self.downloadExtension, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print ("Download %d%%." % int(status.progress() * 100))

    # find id of the buffer folder and get the ids of the files inside
    def getFolderIdByName(self, folderName):
        # get the folder id by folder name
        folderQuery = "mimeType = 'application/vnd.google-apps.folder' and " +"name='" + folderName + "'"
        response = self.service.files().list(q=folderQuery,
                                                spaces='drive',
                                                fields='nextPageToken, files(id, name)').execute()
        folder = response.get('files', [])[0]
        if not folder:
            print('No folders with name ' + folderName + ' found.')
        else:
            folderID = folder.get('id')
            print('Folder ID: ' +  folderID)
        return folderID
        
    def getIdFilesFromFolder(self, folderID):
        # once you have the folder id, get the ids of all the files inside
        folderContentQuery = "mimeType='image/jpeg' and '" + folderID +"' in parents"
        page_token = None
        id_array = []
        while True:
            response = self.service.files().list(q=folderContentQuery,
                                                spaces='drive',
                                                fields='nextPageToken, files(id, name)',
                                                pageToken=page_token).execute()
            for file in response.get('files', []):
                print ('Found file: %s (%s)' % (file.get('name'), file.get('id')))
                id_array.append(file.get('id'))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        return id_array

    def randomStringName(self, N):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=N))

    def uploadFile(self, fileToUpload, folderID):
        fileBaseName = os.path.basename(fileToUpload)
        mime = 'image/png'
        if(os.path.splitext(fileBaseName)[1] == '.mp4'):
            mime = 'video/mp4'
        
        file_metadata = {'name': fileBaseName,
                        'parents' : [folderID]}
        media = MediaFileUpload(fileToUpload, mimetype=mime)
        file = self.service.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id').execute()
        print ('Uploaded file ID: %s' % file.get('id'))

    def deleteFileById(self, file_id):
        try:
            self.service.files().delete(fileId=file_id).execute()
        except:
            print("Could not delete file")
    
    def __init__(self):
        # If modifying these scopes, delete the file token.pickle.
        self.SCOPES = ['https://www.googleapis.com/auth/drive']
        self.downloadExtension = ".jpg"
        self.service = self.setService()
