package it.romanellas.macchinino

import android.Manifest
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat

class MainActivity : AppCompatActivity() {

    private val PERMISSION_REQUEST_CODE = 101
    private lateinit var devicesLayout: LinearLayout
    private val bluetoothAdapter: BluetoothAdapter? = BluetoothAdapter.getDefaultAdapter()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        devicesLayout = findViewById(R.id.devicesLayout)

        if (bluetoothAdapter == null) {
            Toast.makeText(this, "Bluetooth not supported", Toast.LENGTH_LONG).show()
            return
        }

        // Permissions check
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            if (checkSelfPermission(Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(
                    this,
                    arrayOf(Manifest.permission.BLUETOOTH_CONNECT),
                    PERMISSION_REQUEST_CODE
                )
                return
            }
        }

        showPairedDevices()
    }

    private fun showPairedDevices() {
        val permissions = mutableListOf<String>()

        // Android 12+ requires BLUETOOTH_CONNECT
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S &&
            checkSelfPermission(Manifest.permission.BLUETOOTH_CONNECT) != PackageManager.PERMISSION_GRANTED
        ) {
            permissions.add(Manifest.permission.BLUETOOTH_CONNECT)
        }

        // Location permission is still required in some cases (especially for discovery)
        if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            permissions.add(Manifest.permission.ACCESS_FINE_LOCATION)
        }

        if (permissions.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, permissions.toTypedArray(), PERMISSION_REQUEST_CODE)
            return
        }

        val pairedDevices: Set<BluetoothDevice>? = bluetoothAdapter?.bondedDevices

        devicesLayout.removeAllViews() // Clear previous

        if (pairedDevices.isNullOrEmpty()) {
            val tv = TextView(this)
            tv.text = "No paired Bluetooth devices found."
            devicesLayout.addView(tv)
        } else {
            for (device in pairedDevices) {
                val entry = LinearLayout(this).apply {
                    orientation = LinearLayout.VERTICAL
                    setPadding(30, 20, 30, 20)
                    setBackgroundResource(android.R.drawable.dialog_holo_light_frame)
                    setOnClickListener {
                        val intent = Intent(context, CommandActivity::class.java).apply {
                            putExtra("device_name", device.name)
                            putExtra("device_address", device.address) // <== This is used for RFCOMM
                            addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP)
                            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                        }
                        startActivity(intent)
                    }

                    val tv = TextView(this@MainActivity).apply {
                        text = "${device.name ?: "Unknown"}\n${device.address}"
                        textSize = 16f
                        setPadding(30, 20, 30, 20)
                    }

                    addView(tv)

                    // Optional: add margin between cards
                    val params = LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT
                    )
                    params.setMargins(0, 0, 0, 20)
                    layoutParams = params
                }

                devicesLayout.addView(entry)
            }
        }
    }


    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)

        if (requestCode == PERMISSION_REQUEST_CODE) {
            if (grantResults.all { it == PackageManager.PERMISSION_GRANTED }) {
                showPairedDevices()
            } else {
                Toast.makeText(this, "Permissions denied", Toast.LENGTH_SHORT).show()
            }
        }
    }
}
