using System;
using System.Globalization;
using System.Windows.Data;

namespace GoPro.Converters
{
	public class RationalToDouble : IMultiValueConverter
	{
		public object Convert(object[] values, Type targetType, object parameter, CultureInfo culture)
		{
			if (values[0] != null && values[1] != null)
			{
				ulong num = (ulong)values[0];
				ulong num2 = (ulong)values[1];
				return (num2 != 0L) ? ((double)num / (double)num2) : 0.0;
			}
			return null;
		}

		public object[] ConvertBack(object value, Type[] targetTypes, object parameter, CultureInfo culture)
		{
			throw new NotImplementedException();
		}
	}
}
