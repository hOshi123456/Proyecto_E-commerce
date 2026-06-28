from io import BytesIO

from django.http import HttpResponse
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order


def formatear_guaranies(valor):
    valor_entero = int(valor)
    return f"Gs. {valor_entero:,}".replace(",", ".")


class FacturaPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = (
                Order.objects
                .select_related('user', 'cupon')
                .prefetch_related('items')
                .get(
                    id=order_id,
                    user=request.user
                )
            )
        except Order.DoesNotExist:
            return Response(
                {'detail': 'Orden no encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if order.status != Order.STATUS_PAID:
            return Response(
                {
                    'detail': (
                        'La factura solamente puede generarse '
                        'para una orden pagada.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            name='FacturaTitle',
            parent=styles['Title'],
            alignment=TA_CENTER,
            fontSize=20,
            spaceAfter=20,
        )

        elements = []

        elements.append(
            Paragraph(
                'FACTURA DE COMPRA',
                title_style
            )
        )

        fecha_pago = timezone.localtime(
            order.paid_at
        ).strftime('%d/%m/%Y %H:%M')

        datos_cliente = [
            ['Número de orden:', f'#{order.id}'],
            ['Cliente:', order.user.get_full_name() or order.user.username],
            ['Usuario:', order.user.username],
            ['Correo:', order.user.email],
            ['Fecha de pago:', fecha_pago],
            ['Estado:', order.get_status_display()],
        ]

        client_table = Table(
            datos_cliente,
            colWidths=[4 * cm, 11 * cm]
        )

        client_table.setStyle(
            TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ])
        )

        elements.append(client_table)
        elements.append(Spacer(1, 20))

        product_data = [
            [
                'Producto',
                'Variante',
                'Cantidad',
                'Precio unitario',
                'Subtotal',
            ]
        ]

        for item in order.items.all():
            variante = (
                f'{item.variant_size} / '
                f'{item.variant_color}'
            )

            product_data.append([
                item.product_name,
                variante,
                str(item.quantity),
                formatear_guaranies(item.unit_price),
                formatear_guaranies(item.subtotal),
            ])

        product_table = Table(
            product_data,
            colWidths=[
                5 * cm,
                3 * cm,
                2 * cm,
                3 * cm,
                3 * cm,
            ],
            repeatRows=1
        )

        product_table.setStyle(
            TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
            ])
        )

        elements.append(product_table)
        elements.append(Spacer(1, 20))

        totals_data = [
            ['Subtotal:', formatear_guaranies(order.subtotal)],
            [
                'Descuento:',
                formatear_guaranies(order.discount_amount)
            ],
            ['Total:', formatear_guaranies(order.total)],
        ]

        totals_table = Table(
            totals_data,
            colWidths=[11 * cm, 5 * cm]
        )

        totals_table.setStyle(
            TableStyle([
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
                ('TOPPADDING', (0, 0), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ])
        )

        elements.append(totals_table)
        elements.append(Spacer(1, 30))

        elements.append(
            Paragraph(
                'Gracias por su compra.',
                styles['Normal']
            )
        )

        document.build(elements)

        pdf = buffer.getvalue()
        buffer.close()

        response = HttpResponse(
            pdf,
            content_type='application/pdf'
        )

        response['Content-Disposition'] = (
            f'attachment; filename="factura_orden_{order.id}.pdf"'
        )

        return response