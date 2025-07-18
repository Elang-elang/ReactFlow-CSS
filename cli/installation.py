import os
import platform
import subprocess
import urllib.request
import tarfile
import zipfile
import shutil

class NodeJSInstaller:
    def __init__(self):
        self.system = platform.system().lower()
        self.machine = platform.machine().lower()
        self.version = "20.11.0"
        self.base_url = "https://nodejs.org/dist"
        
    def _get_platform_info(self):
        arch_map = {
            'x86_64': 'x64', 'amd64': 'x64', 'i386': 'x86', 'i686': 'x86',
            'armv7l': 'armv7l', 'aarch64': 'arm64', 'arm64': 'arm64'
        }
        
        arch = arch_map.get(self.machine, 'x64')
        
        if self.system == 'windows':
            return f"win-{arch}", "zip"
        elif self.system == 'darwin':
            return f"darwin-{arch}", "tar.gz"
        elif self.system == 'linux':
            return f"linux-{arch}", "tar.xz"
        else:
            return None, None
    
    def _download_file(self, url, filename):
        try:
            urllib.request.urlretrieve(url, filename)
            return True
        except:
            return False
    
    def _extract_file(self, filename):
        try:
            if filename.endswith('.zip'):
                with zipfile.ZipFile(filename, 'r') as zip_ref:
                    zip_ref.extractall('.')
            elif filename.endswith('.tar.gz'):
                with tarfile.open(filename, 'r:gz') as tar_ref:
                    tar_ref.extractall('.')
            elif filename.endswith('.tar.xz'):
                with tarfile.open(filename, 'r:xz') as tar_ref:
                    tar_ref.extractall('.')
            return True
        except:
            return False
    
    def _install_windows(self, folder_name):
        try:
            install_dir = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'nodejs')
            if os.path.exists(install_dir):
                shutil.rmtree(install_dir)
            shutil.move(folder_name, install_dir)
            
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS)
                try:
                    current_path, _ = winreg.QueryValueEx(key, "PATH")
                except FileNotFoundError:
                    current_path = ""
                
                if install_dir not in current_path:
                    new_path = f"{current_path};{install_dir}" if current_path else install_dir
                    winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
                
                winreg.CloseKey(key)
            except:
                pass
            
            return True
        except:
            return False
    
    def _install_unix(self, folder_name):
        try:
            install_dir = os.path.expanduser('~/.local')
            os.makedirs(install_dir, exist_ok=True)
            
            for item in ['bin', 'lib', 'include', 'share']:
                source_path = os.path.join(folder_name, item)
                if os.path.exists(source_path):
                    dest_path = os.path.join(install_dir, item)
                    if os.path.exists(dest_path):
                        shutil.rmtree(dest_path)
                    shutil.copytree(source_path, dest_path)
            
            bin_path = os.path.join(install_dir, 'bin')
            shell_files = ['.bashrc', '.zshrc', '.profile']
            export_line = f'export PATH="{bin_path}:$PATH"'
            
            for shell_file in shell_files:
                profile_path = os.path.join(os.path.expanduser('~'), shell_file)
                if os.path.exists(profile_path):
                    try:
                        with open(profile_path, 'r') as f:
                            content = f.read()
                        if export_line not in content:
                            with open(profile_path, 'a') as f:
                                f.write(f'\n{export_line}\n')
                        break
                    except:
                        continue
            
            return True
        except:
            return False
    
    def _cleanup(self, filename, folder_name):
        try:
            if os.path.exists(filename):
                os.remove(filename)
            if os.path.exists(folder_name):
                shutil.rmtree(folder_name)
        except:
            pass
    
    def _verify_installation(self):
        try:
            node_result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            npm_result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
            return node_result.returncode == 0 and npm_result.returncode == 0
        except:
            return False
    
    def install(self):
        platform_info, ext = self._get_platform_info()
        if not platform_info:
            return False
        
        filename = f"node-v{self.version}-{platform_info}.{ext}"
        url = f"{self.base_url}/v{self.version}/{filename}"
        
        if not self._download_file(url, filename):
            return False
        
        if not self._extract_file(filename):
            self._cleanup(filename, "")
            return False
        
        folder_name = filename.replace(f'.{ext}', '')
        
        if self.system == 'windows':
            success = self._install_windows(folder_name)
        else:
            success = self._install_unix(folder_name)
        
        self._cleanup(filename, folder_name)
        
        if success:
            return self._verify_installation()
        
        return False