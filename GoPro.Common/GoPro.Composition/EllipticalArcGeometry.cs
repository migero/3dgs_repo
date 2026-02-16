using System;
using System.Windows;
using System.Windows.Media;
using System.Windows.Media.Animation;
using GoPro.Composition.Arcs;

namespace GoPro.Composition
{
	public class EllipticalArcGeometry : Animatable
	{
		private Size size;

		private PathGeometry geometry;

		private PathFigure sectorFigure = new PathFigure();

		private PathFigure segmentFigure = new PathFigure();

		private PathFigure ellipseFigure = new PathFigure();

		private ArcSegment arcSegment = new ArcSegment();

		private ArcSegment augmentingArcSegment = new ArcSegment();

		private LineSegment line = new LineSegment();

		private ScaleTransform scaleTransform = new ScaleTransform();

		private RotateTransform rotateTransform = new RotateTransform();

		private static FrameworkPropertyMetadata StrokeOptionsPropertyMetadata = new FrameworkPropertyMetadata((object)EllipticalArcGeometryStrokeOptions.Both, (PropertyChangedCallback)delegate(DependencyObject @object, DependencyPropertyChangedEventArgs eventArgs)
		{
			if (((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_OldValue() != ((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_NewValue())
			{
				((EllipticalArcGeometry)(object)@object).setStrokeOptions((EllipticalArcGeometryStrokeOptions)((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_NewValue());
			}
		});

		public static DependencyProperty StrokeOptionsProperty = DependencyProperty.Register("StrokeOptions", typeof(EllipticalArcGeometryStrokeOptions), typeof(EllipticalArcGeometry), (PropertyMetadata)(object)StrokeOptionsPropertyMetadata);

		private static FrameworkPropertyMetadata CenterPropertyMetadata = new FrameworkPropertyMetadata((object)default(Point), (PropertyChangedCallback)delegate(DependencyObject @object, DependencyPropertyChangedEventArgs eventArgs)
		{
			//IL_001e: Unknown result type (might be due to invalid IL or missing references)
			if (((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_OldValue() != ((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_NewValue())
			{
				((EllipticalArcGeometry)(object)@object).setCenter((Point)((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_NewValue());
			}
		});

		public static DependencyProperty CenterProperty = DependencyProperty.Register("Center", typeof(Point), typeof(EllipticalArcGeometry), (PropertyMetadata)(object)CenterPropertyMetadata);

		private static FrameworkPropertyMetadata RadiusXPropertyMetadata = new FrameworkPropertyMetadata((PropertyChangedCallback)delegate(DependencyObject @object, DependencyPropertyChangedEventArgs eventArgs)
		{
			if (((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_OldValue() != ((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_NewValue())
			{
				((EllipticalArcGeometry)(object)@object).setRadiusX((double)((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_NewValue());
			}
		});

		public static DependencyProperty RadiusXProperty = DependencyProperty.Register("RadiusX", typeof(double), typeof(EllipticalArcGeometry), (PropertyMetadata)(object)RadiusXPropertyMetadata);

		private static FrameworkPropertyMetadata RadiusYPropertyMetadata = new FrameworkPropertyMetadata((PropertyChangedCallback)delegate(DependencyObject @object, DependencyPropertyChangedEventArgs eventArgs)
		{
			if (((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_OldValue() != ((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_NewValue())
			{
				((EllipticalArcGeometry)(object)@object).setRadiusY((double)((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_NewValue());
			}
		});

		public static DependencyProperty RadiusYProperty = DependencyProperty.Register("RadiusY", typeof(double), typeof(EllipticalArcGeometry), (PropertyMetadata)(object)RadiusYPropertyMetadata);

		private static FrameworkPropertyMetadata AnglePropertyMetadata = new FrameworkPropertyMetadata((PropertyChangedCallback)delegate(DependencyObject @object, DependencyPropertyChangedEventArgs eventArgs)
		{
			if (((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_OldValue() != ((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_NewValue())
			{
				((EllipticalArcGeometry)(object)@object).setAngle((double)((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_NewValue());
			}
		});

		public static DependencyProperty AngleProperty = DependencyProperty.Register("Angle", typeof(double), typeof(EllipticalArcGeometry), (PropertyMetadata)(object)AnglePropertyMetadata);

		private static FrameworkPropertyMetadata AngularSizePropertyMetadata = new FrameworkPropertyMetadata((object)360.0, (PropertyChangedCallback)delegate(DependencyObject @object, DependencyPropertyChangedEventArgs eventArgs)
		{
			if (((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_OldValue() != ((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_NewValue())
			{
				((EllipticalArcGeometry)(object)@object).setAngularSize();
			}
		});

		public static DependencyProperty AngularSizeProperty = DependencyProperty.Register("AngularSize", typeof(double), typeof(EllipticalArcGeometry), (PropertyMetadata)(object)AngularSizePropertyMetadata);

		private static FrameworkPropertyMetadata VariantPropertyMetadata = new FrameworkPropertyMetadata((object)EllipticalArcGeometryVariant.Sector, (PropertyChangedCallback)delegate(DependencyObject @object, DependencyPropertyChangedEventArgs eventArgs)
		{
			if (((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_OldValue() != ((DependencyPropertyChangedEventArgs)(ref eventArgs)).get_NewValue())
			{
				((EllipticalArcGeometry)(object)@object).setVariant();
			}
		});

		public static DependencyProperty VariantProperty = DependencyProperty.Register("Variant", typeof(EllipticalArcGeometryVariant), typeof(EllipticalArcGeometry), (PropertyMetadata)(object)VariantPropertyMetadata);

		public EllipticalArcGeometryStrokeOptions StrokeOptions
		{
			get
			{
				return (EllipticalArcGeometryStrokeOptions)((DependencyObject)this).GetValue(StrokeOptionsProperty);
			}
			set
			{
				((DependencyObject)this).SetValue(StrokeOptionsProperty, (object)value);
				setStrokeOptions(value);
			}
		}

		public Point Center
		{
			get
			{
				//IL_000b: Unknown result type (might be due to invalid IL or missing references)
				return (Point)((DependencyObject)this).GetValue(CenterProperty);
			}
			set
			{
				//IL_0006: Unknown result type (might be due to invalid IL or missing references)
				//IL_0012: Unknown result type (might be due to invalid IL or missing references)
				((DependencyObject)this).SetValue(CenterProperty, (object)value);
				setCenter(value);
			}
		}

		public double RadiusX
		{
			get
			{
				return (double)((DependencyObject)this).GetValue(RadiusXProperty);
			}
			set
			{
				((DependencyObject)this).SetValue(RadiusXProperty, (object)value);
				setRadiusX(value);
			}
		}

		public double RadiusY
		{
			get
			{
				return (double)((DependencyObject)this).GetValue(RadiusYProperty);
			}
			set
			{
				((DependencyObject)this).SetValue(RadiusYProperty, (object)value);
				setRadiusY(value);
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
				setAngle(value);
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
				((DependencyObject)this).SetValue(AngularSizeProperty, (object)DefinitionSet.NormalizeAngle(value));
				setAngularSize();
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
				setVariant();
			}
		}

		public EllipticalArcGeometry()
		{
			//IL_0001: Unknown result type (might be due to invalid IL or missing references)
			//IL_000b: Expected O, but got Unknown
			//IL_000c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0016: Expected O, but got Unknown
			//IL_0017: Unknown result type (might be due to invalid IL or missing references)
			//IL_0021: Expected O, but got Unknown
			//IL_0022: Unknown result type (might be due to invalid IL or missing references)
			//IL_002c: Expected O, but got Unknown
			//IL_002d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0037: Expected O, but got Unknown
			//IL_0038: Unknown result type (might be due to invalid IL or missing references)
			//IL_0042: Expected O, but got Unknown
			//IL_0043: Unknown result type (might be due to invalid IL or missing references)
			//IL_004d: Expected O, but got Unknown
			//IL_004e: Unknown result type (might be due to invalid IL or missing references)
			//IL_0058: Expected O, but got Unknown
			//IL_005f: Unknown result type (might be due to invalid IL or missing references)
			//IL_0069: Expected O, but got Unknown
			//IL_0070: Unknown result type (might be due to invalid IL or missing references)
			//IL_011c: Unknown result type (might be due to invalid IL or missing references)
			//IL_0122: Expected O, but got Unknown
			geometry = new PathGeometry();
			sectorFigure.set_StartPoint(Center);
			sectorFigure.set_IsClosed(true);
			((PathSegment)arcSegment).set_IsStroked(true);
			arcSegment.set_SweepDirection((SweepDirection)0);
			((PathSegment)augmentingArcSegment).set_IsStroked(true);
			augmentingArcSegment.set_SweepDirection((SweepDirection)0);
			((PathSegment)line).set_IsStroked(true);
			sectorFigure.get_Segments().Add((PathSegment)(object)line);
			sectorFigure.get_Segments().Add((PathSegment)(object)arcSegment);
			segmentFigure.set_IsClosed(true);
			ellipseFigure.set_IsClosed(true);
			geometry.get_Figures().Add(sectorFigure);
			TransformGroup val = new TransformGroup();
			val.get_Children().Add((Transform)(object)rotateTransform);
			val.get_Children().Add((Transform)(object)scaleTransform);
			((Geometry)geometry).set_Transform((Transform)(object)val);
		}

		protected override Freezable CreateInstanceCore()
		{
			return (Freezable)(object)this;
		}

		public static implicit operator Geometry(EllipticalArcGeometry instance)
		{
			return (Geometry)(object)instance.geometry;
		}

		private void setSegments()
		{
			//IL_0063: Unknown result type (might be due to invalid IL or missing references)
			//IL_0068: Unknown result type (might be due to invalid IL or missing references)
			//IL_0078: Unknown result type (might be due to invalid IL or missing references)
			//IL_007d: Unknown result type (might be due to invalid IL or missing references)
			//IL_008d: Unknown result type (might be due to invalid IL or missing references)
			//IL_0092: Unknown result type (might be due to invalid IL or missing references)
			//IL_00a9: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ae: Unknown result type (might be due to invalid IL or missing references)
			//IL_00d0: Unknown result type (might be due to invalid IL or missing references)
			//IL_00e0: Unknown result type (might be due to invalid IL or missing references)
			//IL_00ec: Unknown result type (might be due to invalid IL or missing references)
			//IL_011c: Unknown result type (might be due to invalid IL or missing references)
			//IL_012a: Unknown result type (might be due to invalid IL or missing references)
			//IL_013c: Unknown result type (might be due to invalid IL or missing references)
			//IL_014c: Unknown result type (might be due to invalid IL or missing references)
			if (Variant != 0)
			{
				geometry.get_Figures().set_Item(0, segmentFigure);
			}
			else
			{
				geometry.get_Figures().set_Item(0, sectorFigure);
			}
			double degrees = AngularSize;
			bool num = AngularSize >= 360.0;
			if (num)
			{
				degrees = 180.0;
			}
			Point center = Center;
			double num2 = ((Point)(ref center)).get_X() + RadiusX;
			center = Center;
			Point val = default(Point);
			((Point)(ref val))._002Ector(num2, ((Point)(ref center)).get_Y());
			center = Center;
			double num3 = ((Point)(ref center)).get_X() + RadiusX * cos(degrees);
			center = Center;
			Point point = default(Point);
			((Point)(ref point))._002Ector(num3, ((Point)(ref center)).get_Y() - RadiusX * sin(degrees));
			sectorFigure.set_StartPoint(Center);
			line.set_Point(val);
			arcSegment.set_Point(point);
			arcSegment.set_IsLargeArc(AngularSize > 180.0);
			if (Variant != 0)
			{
				segmentFigure.set_StartPoint(val);
			}
			if (num)
			{
				ellipseFigure.set_StartPoint(val);
				augmentingArcSegment.set_Size(arcSegment.get_Size());
				augmentingArcSegment.set_Point(val);
				geometry.get_Figures().set_Item(0, ellipseFigure);
			}
		}

		private static double sin(double degrees)
		{
			return Math.Sin(degrees * 2.0 * Math.PI / 360.0);
		}

		private static double cos(double degrees)
		{
			return Math.Cos(degrees * 2.0 * Math.PI / 360.0);
		}

		private void centerTransform()
		{
			scaleTransform.set_CenterX(((Size)(ref size)).get_Width() / 2.0);
			scaleTransform.set_CenterY(((Size)(ref size)).get_Height() / 2.0);
			scaleTransform.set_ScaleY(((Size)(ref size)).get_Height() / ((Size)(ref size)).get_Width());
			rotateTransform.set_CenterX(scaleTransform.get_CenterX());
			rotateTransform.set_CenterY(scaleTransform.get_CenterY());
		}

		private void setCenter(Point value)
		{
			//IL_0014: Unknown result type (might be due to invalid IL or missing references)
			//IL_0025: Unknown result type (might be due to invalid IL or missing references)
			arcSegment.set_Size(new Size(((Point)(ref value)).get_X(), ((Point)(ref value)).get_X()));
			sectorFigure.set_StartPoint(Center);
			centerTransform();
			setSegments();
		}

		private void setRadiusX(double value)
		{
			//IL_0017: Unknown result type (might be due to invalid IL or missing references)
			//IL_001c: Unknown result type (might be due to invalid IL or missing references)
			//IL_003d: Unknown result type (might be due to invalid IL or missing references)
			size = new Size(2.0 * value, ((Size)(ref size)).get_Height());
			arcSegment.set_Size(new Size(((Size)(ref size)).get_Width(), ((Size)(ref size)).get_Width()));
			centerTransform();
			setSegments();
		}

		private void setRadiusY(double value)
		{
			//IL_0017: Unknown result type (might be due to invalid IL or missing references)
			//IL_001c: Unknown result type (might be due to invalid IL or missing references)
			//IL_003d: Unknown result type (might be due to invalid IL or missing references)
			size = new Size(((Size)(ref size)).get_Width(), 2.0 * value);
			arcSegment.set_Size(new Size(((Size)(ref size)).get_Width(), ((Size)(ref size)).get_Width()));
			centerTransform();
			setSegments();
		}

		private void setAngle(double value)
		{
			rotateTransform.set_Angle(0.0 - value);
			setSegments();
		}

		private void setAngularSize()
		{
			setSegments();
		}

		private void setVariant()
		{
			setSegments();
		}

		private void setStrokeOptions(EllipticalArcGeometryStrokeOptions value)
		{
			bool isStroked = (value & EllipticalArcGeometryStrokeOptions.Curve) > EllipticalArcGeometryStrokeOptions.None;
			bool flag = (value & EllipticalArcGeometryStrokeOptions.StraightLines) > EllipticalArcGeometryStrokeOptions.None;
			((PathSegment)arcSegment).set_IsStroked(isStroked);
			((PathSegment)augmentingArcSegment).set_IsStroked(isStroked);
			((PathSegment)line).set_IsStroked(flag);
			sectorFigure.set_IsClosed(flag);
			segmentFigure.set_IsClosed(flag);
		}
	}
}
