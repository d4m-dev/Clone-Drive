import os
import sys
import time
import re
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(open_browser=False, port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

def extract_folder_id_from_url(url):
    pattern = r'[-\w]{25,}'
    match = re.search(pattern, url)
    if match:
        return match.group(0)
    return None

def check_if_exists(service, parent_id, name):
    try:
        name = name.replace("'", "\\'")
        query = f"'{parent_id}' in parents and name = '{name}' and trashed = false"
        response = service.files().list(q=query, fields="files(id)").execute()
        files = response.get('files', [])
        return files[0]['id'] if files else None
    except Exception as e:
        print(f"Error checking file existence: {e}")
        return None

def create_folder(service, parent_id, name):
    folder_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    existing_id = check_if_exists(service, parent_id, name)
    if existing_id:
        return existing_id
    try:
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        return folder.get('id')
    except Exception as e:
        print(f"Error creating folder: {e}")
        return None

def list_files(service, folder_id):
    files = []
    query = f"'{folder_id}' in parents and trashed = false"
    page_token = None
    while True:
        response = service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, mimeType, size)",
            pageToken=page_token,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        files.extend(response.get('files', []))
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return files

def copy_file(service, file, dest_folder_id, total_size, limit_gb):
    if file['mimeType'] != 'application/vnd.google-apps.folder':
        if check_if_exists(service, dest_folder_id, file['name']):
            print(f"[{file['name']}] đã tồn tại. Bỏ qua.")
            return total_size
        try:
            start = time.time()
            copied_file = {
                'parents': [dest_folder_id]
            }
            service.files().copy(fileId=file['id'], body=copied_file, supportsAllDrives=True).execute()
            end = time.time()
            size_mb = int(file.get('size', 0)) / (1024 * 1024)
            total_size += size_mb
            speed = size_mb / max(1e-6, end - start)
            print(f"✓ Đã sao chép {file['name']} ({size_mb:.2f} MB, {speed:.2f} MB/s)")
            if total_size >= (limit_gb * 1024):
                print(f"⚠️ Tổng dung lượng vượt quá {limit_gb} GB. Dừng lại.")
                sys.exit(0)
        except Exception as e:
            print(f"Lỗi khi sao chép: {e}")
    else:
        print(f"📁 Đang tạo thư mục: {file['name']}")
        new_folder_id = create_folder(service, dest_folder_id, file['name'])
        sub_files = list_files(service, file['id'])
        for sub_file in sub_files:
            total_size = copy_file(service, sub_file, new_folder_id, total_size, limit_gb)
    return total_size

def main():
    print("=== 📂 COPY GOOGLE DRIVE TOOL - BY TERMUX ===")
    source_url = input("🔗 Nhập URL thư mục nguồn: ").strip()
    dest_url = input("🔗 Nhập URL thư mục đích: ").strip()
    try:
        limit_gb = float(input("💾 Giới hạn tổng dung lượng (GB, mặc định 700): ").strip() or "700")
    except:
        limit_gb = 700

    service = authenticate()
    source_id = extract_folder_id_from_url(source_url)
    dest_id = extract_folder_id_from_url(dest_url)

    if not source_id or not dest_id:
        print("❌ URL không hợp lệ.")
        return

    source_folder = service.files().get(fileId=source_id, fields='name', supportsAllDrives=True).execute()
    new_folder_id = create_folder(service, dest_id, source_folder['name'])

    files = list_files(service, source_id)
    print(f"📦 Đang sao chép {len(files)} mục từ '{source_folder['name']}'...\n")
    total_size = 0
    for file in files:
        total_size = copy_file(service, file, new_folder_id, total_size, limit_gb)

    print(f"\n✅ Hoàn tất. Tổng dung lượng sao chép: {total_size / 1024:.2f} GB")

if __name__ == "__main__":
    main()
