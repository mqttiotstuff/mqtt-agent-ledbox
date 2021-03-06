/*
 * This Java source file was generated by the Gradle 'init' task.
 */
package fr.frett27.recordvideo;

import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.image.BufferedImage;
import java.awt.image.DataBufferInt;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.LineNumberReader;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JTextArea;
import javax.swing.SwingUtilities;

import org.bytedeco.javacpp.Loader;
import org.bytedeco.opencv.opencv_java;
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.opencv.core.Mat;
import org.opencv.core.Rect;
import org.opencv.imgproc.Imgproc;
import org.opencv.videoio.VideoCapture;
import org.opencv.videoio.VideoWriter;

public class App extends JPanel {

	private static final Rect AOI = new Rect(0, 60, 400, 400);

	private static int MAX_FRAMES = 25 * 12;

	private static VideoCapture videoCapture;

	ScheduledExecutorService video = Executors.newSingleThreadScheduledExecutor();

	Mat m = new Mat();

	private JLabel image;

	private JTextArea mqttCommand = new JTextArea("wave(red)");

	public App() throws Exception {
		initComponents();

		mqttClient = new MqttClient("tcp://mqtt.frett27.net:1883", "myid");
		MqttConnectOptions opt = new MqttConnectOptions();
		opt.setUserName("xxxxxx");
		opt.setPassword("xxxxxx".toCharArray());
		mqttClient.connect(opt);
		mqttClient.setCallback(new MqttCallback() {

			@Override
			public void messageArrived(String topic, MqttMessage message) throws Exception {

			}

			@Override
			public void deliveryComplete(IMqttDeliveryToken token) {

			}

			@Override
			public void connectionLost(Throwable cause) {
				cause.printStackTrace();

			}
		});

		video.scheduleAtFixedRate(() -> {
			try {
				if (active) {
					return;
				}

				videoCapture.read(m);
				Mat m2 = new Mat();

				Rect crop = AOI;

				m2 = m.submat(crop);

				BufferedImage bi = convertOpenCVToJava(m2, 1);

				SwingUtilities.invokeLater(() -> {
					image.setIcon(new ImageIcon(bi));
					repaint();
				});

			} catch (Throwable t) {
				t.printStackTrace();

			}
		}, 1, 1, TimeUnit.SECONDS);

	}

	public static BufferedImage convertOpenCVToJava(Mat m, int resizeFactor) {

		Mat d = new Mat();

		Imgproc.cvtColor(m, d, Imgproc.COLOR_RGB2RGBA, 0);

		// Imgproc.resize(m, d, new Size(m.width() / resizeFactor, m.height() /
		// resizeFactor));

		BufferedImage gray = new BufferedImage(d.width(), d.height(), BufferedImage.TYPE_INT_RGB);
		byte[] rgbcv = new byte[4 * d.height() * d.width()];

		// Get the BufferedImage's backing array and copy the pixels directly into it

		DataBufferInt bdata = (DataBufferInt) gray.getRaster().getDataBuffer();
		int[] data = bdata.getData();

		d.get(0, 0, rgbcv);

		// change image alignment
		for (int i = 0; i < data.length; i++) {
			int r = rgbcv[i * 4] & 0xFF;
			int g = rgbcv[i * 4 + 1] & 0xFF;
			int b = rgbcv[i * 4 + 2] & 0xFF;

			int value = r | g << 8 | b << 16;
			data[i] = value;
		}
		final BufferedImage b = gray;

		return b;
	}

	protected void initComponents() throws Exception {

		setLayout(new BorderLayout());
		image = new JLabel();
		add(image, BorderLayout.CENTER);

		JButton launch = new JButton();
		launch.setText("launch record");

		JPanel btnPanel = new JPanel();
		btnPanel.setLayout(new BorderLayout());
		btnPanel.add(launch, BorderLayout.SOUTH);

		JButton full = new JButton("full");
		full.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				try {
					full();
				} catch (Throwable t) {
					t.printStackTrace();
				}
			};
		});
		
		btnPanel.add(full, BorderLayout.EAST);
		
		mqttCommand.setPreferredSize(new Dimension(600, 200));
		btnPanel.add(mqttCommand, BorderLayout.NORTH);

		add(btnPanel, BorderLayout.SOUTH);

		launch.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				String command = mqttCommand.getText();
				launchRecognition(command);
			}
		});

	}

	boolean active = false;

	private MqttClient mqttClient;

	protected void full() throws Exception {

		try (LineNumberReader fileReader = new LineNumberReader(new FileReader("list.txt"))) {
			String l = null;
			while ((l = fileReader.readLine()) != null) {

				String fileName = l.replaceAll("[\\[\\](), ]", "_");
				File f = new File("out/" + fileName + ".txt");
				if (!f.exists()) {
					System.out.println("handling " + l);
					launchRecognition(l);
				}
			}
		}
	}

	protected void launchRecognition(String command) {

		active = true;
		try {
			VideoWriter videoWriter = new VideoWriter();

			String fileName = command.replaceAll("[\\[\\](), ]", "_");

			FileWriter fw = new FileWriter("out/" + fileName + ".txt");
			fw.write(command);
			fw.close();
			videoWriter.open("out/" + fileName + ".avi", VideoWriter.fourcc('M', 'J', 'P', 'G'), 25, AOI.size());
			Mat m1 = new Mat();
			boolean done = false;
			int i = 0;

			String cmdwithclear = "sequence(" + command + ", clear())";
			
			while (i++ < MAX_FRAMES) {
				videoCapture.read(m);
				if (i > 0.5 * 25 && !done) {
					mqttClient.publish("home/agents/ledbox/run", cmdwithclear.getBytes(), 1, false);
					done = true;
				}

				if (i % 100 == 0) {
					System.out.println(i);
				}

				m1 = m.submat(AOI);

				videoWriter.write(m1);
			}

			videoWriter.release();
		} catch (Throwable t) {
			t.printStackTrace();
		} finally {
			active = false;
		}
	}

	public static void main(String[] args) throws Exception {

		Loader.load(opencv_java.class);

		videoCapture = new VideoCapture();
		if (!videoCapture.open(1)) {
			throw new Exception("Video capture cnnot be opened");
		}

		JFrame f = new JFrame();
		f.getContentPane().setLayout(new BorderLayout());
		f.getContentPane().add(new App());
		f.setSize(200, 400);
		f.setVisible(true);
		f.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		// videoCapture.release();

	}
}
