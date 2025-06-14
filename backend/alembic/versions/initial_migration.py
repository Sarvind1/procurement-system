"""initial migration

Revision ID: 001
Revises: 
Create Date: 2024-03-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE userrole AS ENUM ('admin', 'procurement_manager', 'inventory_manager', 'finance_approver', 'viewer')")
    op.execute("CREATE TYPE productstatus AS ENUM ('active', 'discontinued', 'out_of_stock')")
    op.execute("CREATE TYPE supplierstatus AS ENUM ('active', 'inactive', 'blacklisted', 'pending')")
    op.execute("CREATE TYPE suppliercategory AS ENUM ('manufacturer', 'distributor', 'wholesaler', 'service_provider')")
    op.execute("CREATE TYPE purchaseorderstatus AS ENUM ('draft', 'pending_approval', 'approved', 'ordered', 'partially_received', 'received', 'cancelled')")
    op.execute("CREATE TYPE approvalstatus AS ENUM ('pending', 'approved', 'rejected')")
    op.execute("CREATE TYPE shipmentstatus AS ENUM ('pending', 'in_transit', 'delivered', 'partially_delivered', 'cancelled', 'exception')")
    op.execute("CREATE TYPE shipmenttype AS ENUM ('air', 'sea', 'land', 'rail', 'multimodal')")
    op.execute("CREATE TYPE inventoryadjustmenttype AS ENUM ('receipt', 'issue', 'adjustment', 'return', 'damage')")

    # Create users table
    op.create_table(
        'user',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('admin', 'procurement_manager', 'inventory_manager', 'finance_approver', 'viewer', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, default=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )

    # Create categories table
    op.create_table(
        'category',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('category.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )

    # Create products table
    op.create_table(
        'product',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('sku', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.String(1000), nullable=True),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('category.id'), nullable=False),
        sa.Column('unit_of_measure', sa.String(50), nullable=False),
        sa.Column('cost', sa.Numeric(15, 4), nullable=False),
        sa.Column('price', sa.Numeric(15, 4), nullable=False),
        sa.Column('specifications', postgresql.JSONB, nullable=False, default={}),
        sa.Column('status', sa.Enum('active', 'discontinued', 'out_of_stock', name='productstatus'), nullable=False, default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )

    # Create locations table
    op.create_table(
        'location',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('address', sa.String(500), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )

    # Create inventory table
    op.create_table(
        'inventory',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('product.id'), nullable=False),
        sa.Column('location_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('location.id'), nullable=False),
        sa.Column('quantity_on_hand', sa.Integer(), nullable=False, default=0),
        sa.Column('quantity_reserved', sa.Integer(), nullable=False, default=0),
        sa.Column('reorder_point', sa.Integer(), nullable=False, default=0),
        sa.Column('reorder_quantity', sa.Integer(), nullable=False, default=0),
        sa.Column('last_counted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_movement_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.UniqueConstraint('product_id', 'location_id', name='uq_inventory_product_location')
    )

    # Create suppliers table
    op.create_table(
        'supplier',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('category', sa.Enum('manufacturer', 'distributor', 'wholesaler', 'service_provider', name='suppliercategory'), nullable=False),
        sa.Column('status', sa.Enum('active', 'inactive', 'blacklisted', 'pending', name='supplierstatus'), nullable=False, default='pending'),
        sa.Column('tax_id', sa.String(50), nullable=True),
        sa.Column('payment_terms', sa.Integer(), nullable=False, default=30),
        sa.Column('credit_limit', sa.Numeric(15, 4), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, default='USD'),
        sa.Column('is_preferred', sa.Boolean(), nullable=False, default=False),
        sa.Column('performance_metrics', postgresql.JSONB, nullable=False, default={}),
        sa.Column('notes', sa.String(1000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )

    # Create supplier contacts table
    op.create_table(
        'suppliercontact',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('supplier_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('supplier.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('position', sa.String(100), nullable=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )

    # Create supplier addresses table
    op.create_table(
        'supplieraddress',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('supplier_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('supplier.id'), nullable=False),
        sa.Column('address_type', sa.String(50), nullable=False),
        sa.Column('street_address', sa.String(255), nullable=False),
        sa.Column('city', sa.String(100), nullable=False),
        sa.Column('state', sa.String(100), nullable=False),
        sa.Column('postal_code', sa.String(20), nullable=False),
        sa.Column('country', sa.String(100), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )

    # Create supplier products table
    op.create_table(
        'supplierproduct',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('supplier_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('supplier.id'), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('product.id'), nullable=False),
        sa.Column('supplier_sku', sa.String(100), nullable=False),
        sa.Column('unit_price', sa.Numeric(15, 4), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, default='USD'),
        sa.Column('lead_time_days', sa.Integer(), nullable=False, default=0),
        sa.Column('minimum_order_quantity', sa.Integer(), nullable=False, default=1),
        sa.Column('is_preferred', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )

    # Create purchase orders table
    op.create_table(
        'purchaseorder',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('po_number', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('supplier_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('supplier.id'), nullable=False),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('status', sa.Enum('draft', 'pending_approval', 'approved', 'ordered', 'partially_received', 'received', 'cancelled', name='purchaseorderstatus'), nullable=False, default='draft'),
        sa.Column('order_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expected_delivery_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('total_amount', sa.Numeric(15, 4), nullable=False, default=0),
        sa.Column('currency', sa.String(3), nullable=False, default='USD'),
        sa.Column('terms_and_conditions', sa.String(1000), nullable=True),
        sa.Column('notes', sa.String(500), nullable=True),
        sa.Column('approval_workflow', postgresql.JSONB, nullable=False, default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )

    # Create purchase order items table
    op.create_table(
        'purchaseorderitem',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('purchase_order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('purchaseorder.id'), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('product.id'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(15, 4), nullable=False),
        sa.Column('total_price', sa.Numeric(15, 4), nullable=False),
        sa.Column('received_quantity', sa.Integer(), nullable=False, default=0),
        sa.Column('notes', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )

    # Create purchase order approvals table
    op.create_table(
        'purchaseorderapproval',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('purchase_order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('purchaseorder.id'), nullable=False),
        sa.Column('approver_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'approved', 'rejected', name='approvalstatus'), nullable=False, default='pending'),
        sa.Column('comments', sa.String(500), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )

    # Create shipments table
    op.create_table(
        'shipment',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('shipment_number', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('purchase_order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('purchaseorder.id'), nullable=False),
        sa.Column('carrier', sa.String(100), nullable=False),
        sa.Column('tracking_number', sa.String(100), nullable=True),
        sa.Column('shipment_type', sa.Enum('air', 'sea', 'land', 'rail', 'multimodal', name='shipmenttype'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'in_transit', 'delivered', 'partially_delivered', 'cancelled', 'exception', name='shipmentstatus'), nullable=False, default='pending'),
        sa.Column('shipping_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('estimated_delivery_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('actual_delivery_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('shipping_cost', sa.Numeric(15, 4), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, default='USD'),
        sa.Column('customs_declaration', postgresql.JSONB, nullable=True),
        sa.Column('tracking_updates', postgresql.JSONB, nullable=False, default={}),
        sa.Column('notes', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )

    # Create shipment items table
    op.create_table(
        'shipmentitem',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('shipment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('shipment.id'), nullable=False),
        sa.Column('purchase_order_item_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('purchaseorderitem.id'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(15, 4), nullable=False),
        sa.Column('total_price', sa.Numeric(15, 4), nullable=False),
        sa.Column('customs_value', sa.Numeric(15, 4), nullable=False),
        sa.Column('customs_description', sa.String(500), nullable=True),
        sa.Column('notes', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )

    # Create shipment documents table
    op.create_table(
        'shipmentdocument',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('shipment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('shipment.id'), nullable=False),
        sa.Column('document_type', sa.String(50), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('uploaded_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('notes', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )

    # Create inventory adjustments table
    op.create_table(
        'inventoryadjustment',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('inventory_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('inventory.id'), nullable=False),
        sa.Column('adjusted_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('adjustment_type', sa.Enum('receipt', 'issue', 'adjustment', 'return', 'damage', name='inventoryadjustmenttype'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_cost', sa.Numeric(15, 4), nullable=False),
        sa.Column('reference_number', sa.String(100), nullable=True),
        sa.Column('notes', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'))
    )

def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('inventoryadjustment')
    op.drop_table('shipmentdocument')
    op.drop_table('shipmentitem')
    op.drop_table('shipment')
    op.drop_table('purchaseorderapproval')
    op.drop_table('purchaseorderitem')
    op.drop_table('purchaseorder')
    op.drop_table('supplierproduct')
    op.drop_table('supplieraddress')
    op.drop_table('suppliercontact')
    op.drop_table('supplier')
    op.drop_table('inventory')
    op.drop_table('location')
    op.drop_table('product')
    op.drop_table('category')
    op.drop_table('user')

    # Drop enum types
    op.execute('DROP TYPE inventoryadjustmenttype')
    op.execute('DROP TYPE shipmenttype')
    op.execute('DROP TYPE shipmentstatus')
    op.execute('DROP TYPE approvalstatus')
    op.execute('DROP TYPE purchaseorderstatus')
    op.execute('DROP TYPE suppliercategory')
    op.execute('DROP TYPE supplierstatus')
    op.execute('DROP TYPE productstatus')
    op.execute('DROP TYPE userrole') 