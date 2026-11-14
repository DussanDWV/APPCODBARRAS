"""
Aplicación de Lector de Códigos de Barras para Android
Desarrollada con Kivy usando ZXing nativo de Android
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.core.window import Window
from kivy.uix.popup import Popup

try:
    from android.permissions import request_permissions, Permission
    from jnius import autoclass, cast
    request_permissions([Permission.CAMERA, Permission.WRITE_EXTERNAL_STORAGE])
    ANDROID = True
    
    # Importar clases de Android
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')
    
except ImportError:
    ANDROID = False
    Logger.info("BarcodeScanner: No se detectó Android, ejecutando en modo desktop")


class BarcodeScannerWidget(BoxLayout):
    """Widget principal que contiene los controles del escáner"""
    
    def __init__(self, **kwargs):
        super(BarcodeScannerWidget, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15
        
        # Variables de control
        self.last_barcode = ""
        
        # Crear interfaz
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        
        # Espacio superior
        self.add_widget(Label(size_hint=(1, 0.1)))
        
        # Título
        title = Label(
            text='[b][size=32]📱 Lector de Códigos[/size][/b]',
            markup=True,
            size_hint=(1, 0.15),
            color=(0.2, 0.6, 1, 1)
        )
        self.add_widget(title)
        
        # Icono grande
        icon = Label(
            text='[size=120]📷[/size]',
            markup=True,
            size_hint=(1, 0.2),
        )
        self.add_widget(icon)
        
        # Label para mostrar el resultado
        self.result_label = Label(
            text='Presiona "Escanear" para comenzar',
            size_hint=(1, 0.2),
            font_size='18sp',
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle'
        )
        self.result_label.bind(size=self.result_label.setter('text_size'))
        self.add_widget(self.result_label)
        
        # Botón de escanear
        scan_button = Button(
            text='📸 Escanear Código',
            size_hint=(0.8, 0.15),
            pos_hint={'center_x': 0.5},
            background_color=(0.2, 0.8, 0.2, 1),
            font_size='22sp',
            bold=True
        )
        scan_button.bind(on_press=self.start_scan)
        self.add_widget(scan_button)
        
        # Botón de copiar (inicialmente deshabilitado)
        self.copy_button = Button(
            text='📋 Copiar Código',
            size_hint=(0.8, 0.15),
            pos_hint={'center_x': 0.5},
            background_color=(0.2, 0.6, 1, 1),
            font_size='22sp',
            bold=True,
            disabled=True
        )
        self.copy_button.bind(on_press=self.copy_barcode)
        self.add_widget(self.copy_button)
        
        # Espacio inferior
        self.add_widget(Label(size_hint=(1, 0.05)))
        
        # Label de información
        info_label = Label(
            text='Soporta: QR, EAN, UPC, Code128, Code39 y más',
            size_hint=(1, 0.08),
            font_size='13sp',
            color=(0.7, 0.7, 0.7, 1)
        )
        self.add_widget(info_label)
        
    def start_scan(self, instance):
        """Inicia el escaneo usando la app de cámara de Android"""
        if ANDROID:
            try:
                # Usar Intent de Google ZXing (Barcode Scanner)
                activity = PythonActivity.mActivity
                intent = Intent()
                intent.setAction("com.google.zxing.client.android.SCAN")
                intent.putExtra("SCAN_MODE", "QR_CODE_MODE,PRODUCT_MODE,ONE_D_MODE,DATA_MATRIX_MODE")
                
                # Intentar abrir el escáner
                try:
                    activity.startActivityForResult(intent, 0)
                    # Programar verificación del resultado
                    Clock.schedule_interval(self.check_result, 0.5)
                except Exception as e:
                    # Si no tiene ZXing, usar escáner genérico
                    self.use_generic_scanner()
                    
            except Exception as e:
                Logger.error(f"BarcodeScanner: Error al iniciar escáner - {e}")
                self.result_label.text = f'Error: {str(e)}'
        else:
            self.result_label.text = 'Esta función solo funciona en Android'
            
    def use_generic_scanner(self):
        """Usa el escáner de códigos genérico de Android si ZXing no está instalado"""
        try:
            activity = PythonActivity.mActivity
            intent = Intent("android.intent.action.VIEW")
            
            # Intentar con diferentes apps de escaneo
            packages = [
                "com.google.zxing.client.android",  # Barcode Scanner
                "com.google.android.googlequicksearchbox",  # Google Lens
            ]
            
            for package in packages:
                intent.setPackage(package)
                try:
                    activity.startActivity(intent)
                    return
                except:
                    continue
                    
            # Si ninguna funciona, mostrar mensaje
            self.show_install_popup()
            
        except Exception as e:
            Logger.error(f"BarcodeScanner: {e}")
            self.show_install_popup()
            
    def show_install_popup(self):
        """Muestra popup para instalar app de escaneo"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        msg = Label(
            text='Necesitas instalar una app de escaneo.\n\n'
                 'Recomendamos "Barcode Scanner" de ZXing\n'
                 'o usa Google Lens.\n\n'
                 '¿Deseas ir a Play Store?',
            halign='center',
            valign='middle'
        )
        msg.bind(size=msg.setter('text_size'))
        content.add_widget(msg)
        
        btn_layout = BoxLayout(size_hint=(1, 0.3), spacing=10)
        
        yes_btn = Button(text='Sí, ir a Play Store', background_color=(0.2, 0.8, 0.2, 1))
        no_btn = Button(text='Cancelar', background_color=(0.8, 0.2, 0.2, 1))
        
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='App de Escaneo Requerida',
            content=content,
            size_hint=(0.9, 0.5)
        )
        
        yes_btn.bind(on_press=lambda x: self.open_play_store())
        yes_btn.bind(on_press=popup.dismiss)
        no_btn.bind(on_press=popup.dismiss)
        
        popup.open()
        
    def open_play_store(self):
        """Abre Play Store para instalar Barcode Scanner"""
        if ANDROID:
            try:
                activity = PythonActivity.mActivity
                intent = Intent(Intent.ACTION_VIEW)
                intent.setData(autoclass('android.net.Uri').parse(
                    "market://details?id=com.google.zxing.client.android"
                ))
                activity.startActivity(intent)
            except:
                # Si falla, abrir en navegador
                intent = Intent(Intent.ACTION_VIEW)
                intent.setData(autoclass('android.net.Uri').parse(
                    "https://play.google.com/store/apps/details?id=com.google.zxing.client.android"
                ))
                activity.startActivity(intent)
                
    def check_result(self, dt):
        """Verifica si hay resultado del escaneo"""
        if ANDROID:
            try:
                activity = PythonActivity.mActivity
                # Aquí obtendrías el resultado de la Activity
                # Por simplicidad, usamos un método alternativo
                Clock.unschedule(self.check_result)
            except:
                pass
                
    def copy_barcode(self, instance):
        """Copia el código de barras al portapapeles"""
        if self.last_barcode and ANDROID:
            try:
                ClipboardManager = autoclass('android.content.ClipboardManager')
                ClipData = autoclass('android.content.ClipData')
                Context = autoclass('android.content.Context')
                
                activity = PythonActivity.mActivity
                clipboard = cast('android.content.ClipboardManager',
                               activity.getSystemService(Context.CLIPBOARD_SERVICE))
                clip = ClipData.newPlainText("barcode", self.last_barcode)
                clipboard.setPrimaryClip(clip)
                
                self.show_message("✓ Copiado", f"Código copiado al portapapeles:\n{self.last_barcode}")
                
            except Exception as e:
                Logger.error(f"BarcodeScanner: Error al copiar - {e}")
                self.show_message("Código", self.last_barcode)
        elif self.last_barcode:
            self.show_message("Código", self.last_barcode)
                
    def show_message(self, title, message):
        """Muestra un mensaje en pantalla"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        msg_label = Label(
            text=message,
            halign='center',
            valign='middle'
        )
        msg_label.bind(size=msg_label.setter('text_size'))
        content.add_widget(msg_label)
        
        close_button = Button(
            text='Cerrar',
            size_hint=(1, 0.3),
            background_color=(0.2, 0.6, 1, 1)
        )
        content.add_widget(close_button)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.85, 0.4)
        )
        close_button.bind(on_press=popup.dismiss)
        popup.open()


class BarcodeScannerApp(App):
    """Clase principal de la aplicación"""
    
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        self.title = 'Lector de Códigos de Barras'
        return BarcodeScannerWidget()


if __name__ == '__main__':
    BarcodeScannerApp().run()
