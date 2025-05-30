<h1>📂 Copy Drive bằng Python (không dùng Colab)</h1>

  <h2>✅ 1. Bật Google Drive API và lấy credentials</h2>
  <ol>
    <li>Truy cập: <a href="https://console.cloud.google.com" target="_blank">https://console.cloud.google.com</a></li>
    <li>Tạo một <strong>project mới</strong>.</li>
    <li>Đi tới <strong>API & Services → Library</strong> → tìm và bật <code>Google Drive API</code>.</li>
    <li>Vào <strong>Credentials → Create Credentials</strong> → chọn <code>OAuth client ID</code>.</li>
    <li>Chọn loại ứng dụng là <strong>Desktop App</strong>.</li>
    <li>Tải về file <code>credentials.json</code>.</li>
    <li>Đặt file đó vào cùng thư mục với file <code>copy_drive.py</code>.</li>
  </ol>

  <h2>✅ 2. Lấy file về máy<code>requirements.txt
  copy-drive.py</code></h2>
  <pre><code>git clone https//:github.com/d4m-dev/Clone-Drive.git</code></pre>
  <pre><code>cd Clone-Drive
ls</code></pre>
  <h3>Bạn sẽ thấy tất cả file cần thiết để chạy</h3>

  <h2>✅ 3. Cài thư viện</h2>
  <pre><code>pip install -r requirements.txt</code></pre>

  <h2>✅ 4. Chạy chương trình</h2>
  <pre><code>python copy_drive.py</code></pre>

  <h2>✅ 5. Giao diện dòng lệnh</h2>
  <p>Chương trình sẽ yêu cầu bạn nhập 2 liên kết:</p>
  <ul>
    <li>🔗 URL thư mục <strong>nguồn</strong> (Google Drive shared/folder gốc)</li>
    <li>🔗 URL thư mục <strong>đích</strong> (thư mục Google Drive của bạn)</li>
  </ul>
  <p>Sau đó chương trình sẽ:</p>
  <ul>
    <li>✅ Xác thực người dùng qua trình duyệt.</li>
    <li>✅ Tạo thư mục đích mới (tên giống thư mục nguồn).</li>
    <li>✅ Sao chép toàn bộ file & folder bên trong.</li>
    <li>✅ Hiển thị tiến trình và tốc độ sao chép.</li>
  </ul>

  <h2>📌 Ghi chú</h2>
  <ul>
    <li>Chương trình hỗ trợ <strong>Google Drive cá nhân và Drive chia sẻ</strong>.</li>
    <li>Thao tác được trên các file và thư mục lồng nhau.</li>
    <li>Không yêu cầu Google Colab.</li>
  </ul>

  <footer>
    <hr>
    <p><em>Powered by Python & Google Drive API</em></p>
  </footer>
  
