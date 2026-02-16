using System.Windows;
using System.Windows.Media;
using System.Windows.Shapes;
using GoPro.Composition.Arcs;

namespace GoPro.Composition
{
	public class EllipticalArcShape : Shape
	{
		private EllipticalArcGeometry geometry = new EllipticalArcGeometry();

		private static FrameworkPropertyMetadata StrokeOptionsPropertyMetadata = new FrameworkPropertyMetadata((object)EllipticalArcGeometryStrokeOptions.Both, (PropertyChangedCallback)delegate(DependencyObject @object, DependencyPropertyChangedEventArgs eventArgs)
		{
			if (((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_OldValue() != ((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_NewValue())
			{
				((EllipticalArcShape)(object)@object).geometry.StrokeOptions = (EllipticalArcGeometryStrokeOptions)((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_NewValue();
			}
		});

		public static DependencyProperty StrokeOptionsProperty = DependencyProperty.Register("StrokeOptions", typeof(EllipticalArcGeometryStrokeOptions), typeof(EllipticalArcShape), (PropertyMetadata)(object)StrokeOptionsPropertyMetadata);

		private static FrameworkPropertyMetadata AnglePropertyMetadata = new FrameworkPropertyMetadata((PropertyChangedCallback)delegate(DependencyObject @object, DependencyPropertyChangedEventArgs eventArgs)
		{
			if (((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_OldValue() != ((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_NewValue())
			{
				((EllipticalArcShape)(object)@object).geometry.Angle = (double)((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_NewValue();
			}
		});

		public static DependencyProperty AngleProperty = DependencyProperty.Register("Angle", typeof(double), typeof(EllipticalArcShape), (PropertyMetadata)(object)AnglePropertyMetadata);

		private static FrameworkPropertyMetadata AngularSizePropertyMetadata = new FrameworkPropertyMetadata((object)360.0, (PropertyChangedCallback)delegate(DependencyObject @object, DependencyPropertyChangedEventArgs eventArgs)
		{
			if (((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_OldValue() != ((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_NewValue())
			{
				((EllipticalArcShape)(object)@object).geometry.AngularSize = (double)((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_NewValue();
			}
		});

		public static DependencyProperty AngularSizeProperty = DependencyProperty.Register("AngularSize", typeof(double), typeof(EllipticalArcShape), (PropertyMetadata)(object)AngularSizePropertyMetadata);

		private static FrameworkPropertyMetadata VariantPropertyMetadata = new FrameworkPropertyMetadata((object)EllipticalArcGeometryVariant.Sector, (PropertyChangedCallback)delegate(DependencyObject @object, DependencyPropertyChangedEventArgs eventArgs)
		{
			if (((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_OldValue() != ((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_NewValue())
			{
				((EllipticalArcShape)(object)@object).geometry.Variant = (EllipticalArcGeometryVariant)((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_NewValue();
			}
		});

		public static DependencyProperty VariantProperty = DependencyProperty.Register("Variant", typeof(EllipticalArcGeometryVariant), typeof(EllipticalArcShape), (PropertyMetadata)(object)VariantPropertyMetadata);

		protected override Geometry DefiningGeometry => geometry;

		public EllipticalArcGeometryStrokeOptions StrokeOptions
		{
			get
			{
				return (EllipticalArcGeometryStrokeOptions)((DependencyObject)this).GetValue(StrokeOptionsProperty);
			}
			set
			{
				((DependencyObject)this).SetValue(StrokeOptionsProperty, (object)value);
				geometry.StrokeOptions = value;
			}
		}

		public double Angle
		{
			get
			{
				return (double)((DependencyObject)this).GetValue(AngleProperty);
			}
			set
			{
				((DependencyObject)this).SetValue(AngleProperty, (object)value);
				geometry.Angle = value;
			}
		}

		public double AngularSize
		{
			get
			{
				return (double)((DependencyObject)this).GetValue(AngularSizeProperty);
			}
			set
			{
				double num = DefinitionSet.NormalizeAngle(value);
				((DependencyObject)this).SetValue(AngularSizeProperty, (object)num);
				geometry.AngularSize = num;
			}
		}

		public EllipticalArcGeometryVariant Variant
		{
			get
			{
				return (EllipticalArcGeometryVariant)((DependencyObject)this).GetValue(VariantProperty);
			}
			set
			{
				((DependencyObject)this).SetValue(VariantProperty, (object)value);
				geometry.Variant = value;
			}
		}

		public EllipticalArcShape()
		{
			//IL_0018: Unknown result type (might be due to invalid IL or missing references)
			//IL_0026: Unknown result type (might be due to invalid IL or missing references)
			//IL_0030: Expected O, but got Unknown
			((Shape)this).set_StrokeLineJoin((PenLineJoin)1);
			new Rectangle();
			((FrameworkElement)this).add_SizeChanged((SizeChangedEventHandler)delegate
			{
				//IL_0058: Unknown result type (might be due to invalid IL or missing references)
				((FrameworkElement)this).BeginInit();
				geometry.RadiusX = ((FrameworkElement)this).get_ActualWidth() / 2.0;
				geometry.RadiusY = ((FrameworkElement)this).get_ActualHeight() / 2.0;
				geometry.Center = new Point(geometry.RadiusX, geometry.RadiusY);
				((FrameworkElement)this).EndInit();
			});
		}
	}
}
