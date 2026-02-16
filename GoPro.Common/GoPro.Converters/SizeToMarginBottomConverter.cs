using System;
using System.Globalization;
using System.Windows;
using System.Windows.Data;

namespace GoPro.Converters
{
	public class SizeToMarginBottomConverter : IMultiValueConverter
	{
		public object Convert(object[] values, Type targetType, object parameter, CultureInfo culture)
		{
			//IL_0042: Unknown result type (might be due to invalid IL or missing references)
			double num = (double)values[0];
			double num2 = (double)values[1];
			double num3 = (double)values[2];
			double num4 = (double)values[3];
			double num5 = (double)values[4];
			double num6 = (double)values[5] + (num - num2);
			return (object)new Thickness(num3, num4, num5, num6);
		}

		public object[] ConvertBack(object value, Type[] targetTypes, object parameter, CultureInfo culture)
		{
			throw new NotImplementedException();
		}
	}
}
