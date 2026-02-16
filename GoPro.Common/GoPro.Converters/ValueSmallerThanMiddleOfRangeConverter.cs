using System;
using System.Globalization;
using System.Windows.Data;

namespace GoPro.Converters
{
	public class ValueSmallerThanMiddleOfRangeConverter : IMultiValueConverter
	{
		public object Convert(object[] values, Type targetType, object parameter, CultureInfo culture)
		{
			double num = ((values[0].GetType() == typeof(double)) ? ((double)values[0]) : 0.0);
			double num2 = ((values[1].GetType() == typeof(double)) ? ((double)values[1]) : 0.0);
			double num3 = ((values[2].GetType() == typeof(double)) ? ((double)values[2]) : 0.0);
			if (num < (num3 - num2) / 2.0)
			{
				return true;
			}
			return false;
		}

		public object[] ConvertBack(object value, Type[] targetTypes, object parameter, CultureInfo culture)
		{
			throw new NotImplementedException();
		}
	}
}
