import os
import re
import time
import sys
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)


def extract_id_from_url(url):
    match = re.search(r'[-\w]{25,}', url)
    return match.group(0) if match else None


def get_folder_name(service, folder_id):
    folder = service.files().get(fileId=folder_id, supportsAllDrives=True).execute()
    return folder['name']


def list_files(service, folder_id):
    files = []
    page_token = None
    while True:
        response = service.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            fields='nextPageToken, files(id, name, mimeType, size)',
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            pageToken=page_token
        ).execute()
        files.extend(response.get('files', []))
        page_token = response.get('nextPageToken', None)
        if not page_token:
            break
    return files


def create_folder(service, name, parent_id):
    query = f"'{parent_id}' in parents and name = '{name}' and mimeType = 'application/vnd.google-apps.folder'"
    results = service.files().list(q=query, fields="files(id)", supportsAllDrives=True).execute()
    if results['files']:
        return results['files'][0]['id']
    folder_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    folder = service.files().create(body=folder_metadata, fields='id', supportsAllDrives=True).execute()
    return folder['id']


def file_exists(service, parent_id, name):
    query = f"'{parent_id}' in parents and name = '{name}' and trashed = false"
    results = service.files().list(q=query, fields="files(id)", supportsAllDrives=True).execute()
    return len(results['files']) > 0


def copy_file(service, file_id, name, parent_id):
    if file_exists(service, parent_id, name):
        print(f"[{name}] đã tồn tại, bỏ qua.")
        return
    body = {'name': name, 'parents': [parent_id]}
    service.files().copy(fileId=file_id, body=body, supportsAllDrives=True).execute()
    print(f"Đã sao chép: {name}")


def copy_folder(service, source_folder_id, dest_folder_id):
    items = list_files(service, source_folder_id)
    for item in items:
        name = item['name']
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            print(f"📁 Vào thư mục: {name}")
            new_folder_id = create_folder(service, name, dest_folder_id)
            copy_folder(service, item['id'], new_folder_id)
        else:
            copy_file(service, item['id'], name, dest_folder_id)


def main():
    source_url = input("Nhập URL thư mục nguồn: ").strip()
    dest_url = input("Nhập URL thư mục đích: ").strip()

    source_id = extract_id_from_url(source_url)
    dest_id = extract_id_from_url(dest_url)

    if not source_id or not dest_id:
        print("❌ Không tìm thấy ID hợp lệ trong URL.")
        sys.exit(1)

    service = authenticate()
    folder_name = get_folder_name(service, source_id)
    new_folder_id = create_folder(service, folder_name, dest_id)

    print(f"🚀 Bắt đầu sao chép từ [{folder_name}]...")
    start = time.time()
    copy_folder(service, source_id, new_folder_id)
    end = time.time()

    print(f"✅ Hoàn tất! Thời gian: {int(end - start)} giây.")


if __name__ == '__main__':
    main()
