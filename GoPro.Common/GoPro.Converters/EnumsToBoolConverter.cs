using System;
using System.Globalization;
using System.Windows.Data;

namespace GoPro.Converters
{
	public class EnumsToBoolConverter : IMultiValueConverter
	{
		public object Convert(object[] values, Type targetType, object parameter, CultureInfo culture)
		{
			int num = (int)values[0];
			for (int i = 1; i < values.Length; i++)
			{
				if (num == (int)values[i])
				{
					return true;
				}
			}
			return false;
		}

		public object[] ConvertBack(object value, Type[] targetTypes, object parameter, CultureInfo culture)
		{
			throw new NotImplementedException();
		}
	}
}
