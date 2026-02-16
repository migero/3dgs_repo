using System;
using System.Globalization;
using System.Windows.Data;

namespace GoPro.Converters
{
	public class BoolsAndToBoolConverter : IMultiValueConverter
	{
		public object Convert(object[] values, Type targetType, object parameter, CultureInfo culture)
		{
			bool flag = bool.Parse((string)parameter);
			for (int i = 0; i < values.Length; i++)
			{
				if ((bool)values[i] != flag)
				{
					return false;
				}
			}
			return true;
		}

		public object[] ConvertBack(object value, Type[] targetTypes, object parameter, CultureInfo culture)
		{
			throw new NotImplementedException();
		}
	}
}
