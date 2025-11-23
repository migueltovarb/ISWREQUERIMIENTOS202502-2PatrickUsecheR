from django.core.mail import send_mail

def enviar_notificacion_estado(usuario_email, tipo_objeto, codigo, nuevo_estado):
    asunto = f'RESOLUCION ESTADO RECLAMO/SOLICITUD'
    mensaje = (
        f'Hola,\n\n'
        f'Tu {tipo_objeto} con código {codigo} ha cambiado de estado a: {nuevo_estado}. \n\n'
    )
    send_mail(
        asunto,
        mensaje,
        'tu_correo@gmail.com',  # remitente
        [usuario_email],
        fail_silently=False,
    )